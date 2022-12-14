from cgi import print_arguments
from tkinter import CASCADE
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, String, BLOB, ForeignKey, UniqueConstraint, Table, PrimaryKeyConstraint
from app.database import Base, engine

# https://towardsdatascience.com/use-flask-and-sqlalchemy-not-flask-sqlalchemy-5a64fafe22a4

class BaseModel(Base):
    __abstract__ = True
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def to_json(self):
        return self.to_dict().as_dict()
    pass

class User(BaseModel):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(500), nullable=False)
    email = Column(String(200), unique=True)
    
# class FileTags(BaseModel):
#     __tablename__ = "file_tags"
#     file_id = Column(Integer, primary_key=True, index=True)
#     tag_name = Column(String(64), primary_key=True, index=True)
#     tag_value = Column(String(1024), nullable=True)
    
class File(BaseModel):
    """File is an association class between User and PhysicalFile.
    It acts as a symlink. """
    __tablename__ = "file"

    id = Column(Integer, primary_key=True, index=True)
    md5 = Column(String(32), ForeignKey('physicalfile.md5', name='fk_file_physicalfile'), unique=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id', name='fk_file_user'))
    name = Column(String(128))
    
    user_md5_unique = UniqueConstraint(user_id, md5, name='unq_file')
    user = relationship('User', backref='files')
    

class PhysicalFile(BaseModel):
    __tablename__ = "physicalfile"
    
    md5 = Column(String(32), primary_key=True, index=True)
    path = Column(String(512))

    
class BaseFeatureSet(BaseModel):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    # foreign keys
    @declared_attr
    def owner_id(cls):
        return Column(Integer, ForeignKey('user.id', name=f'fk_{cls.__name__.lower()}_user'))
    @declared_attr
    def file_id(cls):
        return Column(Integer, ForeignKey('file.id', name=f'fk_{cls.__name__.lower()}_file'))
    @declared_attr
    def tagset_id(cls):
        return Column(Integer, ForeignKey('tagsset.id', name=f'fk_{cls.__name__.lower()}_tagset'), nullable=True)
    
    # relationships
    @declared_attr
    def owner(cls):
        return relationship('User', backref=f'{cls.__name__.lower()}_list')
    @declared_attr
    def file(cls):
        return relationship('File', backref=f'{cls.__name__.lower()}')
    @declared_attr
    def tags(cls):
        return relationship('TagsSet', backref=f'{cls.__name__.lower()}_list')
        
    @declared_attr
    def __mapper_args__(cls):
        """adds the __mapper_args__ dunder var to every object inherting from this
        class. every table inherting needs to be declared as polymorphic"""

        if cls.__name__ != "BaseFeatureSet":
            return {"polymorphic_identity": cls.__name__.lower(), "concrete": True}
        else:
            return {}
    
class RegionSet(BaseFeatureSet):
    __tablename__ = "regionset"
    pass

class Feature1D(BaseFeatureSet):
    __tablename__ = 'feature1d'
    pass

class Feature2D(BaseFeatureSet):
    __tablename__ = 'feature2d'
    pass
    

class Calculation(BaseModel):
    __abstract__ = True
    _feature_class = BaseFeatureSet # change this when inheriting
    
    id = Column(Integer, primary_key=True, index=True)
    windowsize = Column(Integer, default='var')
    binsize = Column(Integer, nullable=False)
    
    # columns
    @declared_attr
    def regionset_id(cls):
        return Column(Integer, ForeignKey('regionset.id', name=f'fk_{cls.__name__.lower()}_regionset'), nullable=False, index=True)
    
    @declared_attr
    def owner_id(cls):
        return Column(Integer, ForeignKey('user.id', name=f'fk_{cls.__name__.lower()}_user'), nullable=False)
    
    # @declared_attr
    # def directory_id(cls):
    #     return Column(Integer, ForeignKey('directory.id', name=f'fk_{cls.__name__.lower()}_dir'))
    
    @declared_attr
    def task_id(cls):
        return Column(Integer, ForeignKey('task.id', name=f'fk_{cls.__name__.lower()}_task'))
    
    # candidate key constraint
    @declared_attr
    def candidate_key_constraint(cls):
        return UniqueConstraint(cls.regionset_id, cls.windowsize, cls.owner_id, name=f'unique_{cls.__name__.lower()}')
    
    # relationships
    @declared_attr
    def regionset(cls):
        return relationship('RegionSet', backref=f'{cls.__name__.lower()}s')
    
    @declared_attr
    def owner(cls):
        return relationship('User', backref=f'{cls.__name__.lower()}s')
    
    # @declared_attr
    # def directory(cls):
    #     return relationship('Directory', backref=f'{cls.__name__.lower()}s')

class Task(BaseModel):
    __tablename__ = 'task'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, unique=True) # TODO meeeeh
    

class LinegraphCalculation(Calculation):
    __tablename__ = 'calc_linegraph'
    _feature_class = Feature1D


class LolaCalculation(Calculation):
    __tablename__ = 'calc_lola'
    _feature_class = RegionSet


class Umap1DCalculation(Calculation):
    __tablename__ = 'calc_umap1d'
    _feature_class = Feature1D


class Umap2DCalculation(Calculation):
    __tablename__ = 'calc_umap2d'
    _feature_class = Feature2D


class StackedLineprofileCalculation(Calculation):
    __tablename__ = 'calc_stackup'
    _feature_class = Feature1D


class HeatmapCalculation(Calculation):
    __tablename__ = 'calc_heatmap'
    _feature_class = Feature2D
    

class _association_calculation_feature(BaseModel):
    """abstract class to make many-to-many relationships (collections)"""
    __abstract__ = True
    _c = None  # calulation_class
    _f = None  # feature_class
    
    @property
    def _cn(cls):
        return cls._c.__name__.lower()
    @property
    def _fn(cls):
        return cls._f.__name__.lower()
        
    @declared_attr
    def calculation_id(cls):
        return Column(
            Integer,
            ForeignKey(
                f'{cls._c.__tablename__}.id',
                name=f'fk_{cls.__tablename__}_{cls._c.__name__.lower()}'
                ), 
            primary_key=True
        )
    @declared_attr
    def feature_id(cls):
        return Column(
            Integer,
            ForeignKey(
                f'{cls._f.__tablename__}.id',
                name=f'fk_{cls.__tablename__}_{cls._f.__name__.lower()}'
                ), 
            primary_key=True
        )
    @declared_attr
    def calculation(cls):
        return relationship(cls._c, backref='features')
    @declared_attr
    def feature(cls):
        return relationship(cls._f, backref=f'{cls._c}s')
    @declared_attr
    def primary_key(cls):
        return PrimaryKeyConstraint("data_id", "feature_id", name=f'pk_{cls.__tablename__}')
    

# create nr of feature associations
# TODO check out warnings produced, should be neglible
def _assoc_creator(calculation_cls, feature_cls):
    tablename = f'assoc_{calculation_cls.__name__.lower()}_{feature_cls.__name__.lower()}'
    
    class _T(_association_calculation_feature):
        _c = calculation_cls
        _f = feature_cls
        __tablename__ = tablename
    _T.__name__ = tablename
    return _T

_calculation_models = [LinegraphCalculation, Umap2DCalculation, LolaCalculation] # add more
for calc_cls in _calculation_models:
    _assoc_creator(calc_cls, calc_cls._feature_class) # not assigned to anything as attached to base metadata

class TagsSet(BaseModel):
    __tablename__ = 'tagsset'
    
    id = Column(Integer, primary_key=True)
    tag_name = Column(String(50), nullable=False)
    tag_value = Column(String(500), nullable=True)
    
    candidate_key = UniqueConstraint(tag_name, tag_value, 'unique_tagname_tagvalue')

Base.metadata.create_all(engine, checkfirst=True)



# class File_Group(BaseModel):
#     __tablename__ = "assoc_file_group"
#     physical_file_id = Column(Integer, primary_key=True, index=True)
#     owner_id = Column(Integer, primary_key=True, index=True)
#     group_id = Column(Integer, ForeignKey('group.id', name='fk_groupsymlink_user'), primary_key=True, index=True)
#     may_edit = Column(Boolean, default=True)
#     fk_symlink = ForeignKeyConstraint([physical_file_id, owner_id], ["physicalfile.id", "physicalfile.owner_id"], name='fk_usersymlinkgroup_symlink')

# class User_Group(BaseModel):
#     __tablename__ = "assoc_user_group"
#     user_id = Column(Integer, ForeignKey('user.id', name='fk_usergroup_user'), primary_key=True, index=True)
#     group_id = Column(Integer, ForeignKey('group.id', name='fk_usergroup_group'), primary_key=True, index=True)
#     permissions = Column(String(50), nullable=True) # use some enum or smth like that

# class User(BaseModel):
#     __tablename__ = "user"
    
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String(50), unique=True)
#     password_hash = Column(String(500), nullable=False)
#     email = Column(String(200), unique=True)
    
#     files = relationship('file', backref='creator')
#     api_keys = relationship('apikey', backref='user')
#     groups_created = relationship('group', backref='creator')
#     group_memberships = relationship('group', backref='users', secondary=User_Group)
