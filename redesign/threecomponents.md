Drei Komponenten:
    Controller - DB, Webserver, evtl jupyterhub o.ä.?
    Executor - führt (Python) code aus der an ihn gesendet wird
    Speicher - Speicherort e.g. Cloud, Local, whatever


Controller:
    Webserver mit Routen und Objekten
    Führt Processings aus

Executor:
    Executor(FileStorage):
        run(function)

    LocalExecutor
    SLURMExecutor
    AWSExecutor

FileStorage:
    FileStorage(conf):
        open(...) -> fh

    LocalFileStorage
    SSHFileStorage
    ...

Controller bekommt "Files" die berechnet werden sollen:
    Hashes werden berechnet und an Controller geschickt
    Controller checkt ob hashes in der File-Table sind.
    Schickt zurück welche er schon hat und welche noch fehlen.
    Die fehlenden Dateien werden hochgeladen und, wenn der hash stimmt und sie validaten, gespeichert.
    Dann werden für diesen Satz an Files berechnungen durchgeführt.
    Woher weiß der Controller ob es schon eine Berechnung mit diesem Datensatz existiert?
        zB Linegraph: <-- regionsethash, featurehash
            (regionsethash + featurehash + "linegraph").hash()
        zB Embedding1D: regionsethash, [featurehash,...]
            ((regionsethash + featurehash + ...) + "embedding1d").hash()

