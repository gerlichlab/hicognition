<template>
    <div>
    <b-list-group>
      <b-list-group-item>
        <b-button
          variant="link"
          class="text-left w-100"
          v-b-toggle.collapse-regions
        >
          <b-icon icon="grid-3x3-gap"></b-icon> Regions
        </b-button>
      </b-list-group-item>
        <b-collapse id="collapse-regions">
          <b-list-group flush>
            <b-list-group-item class="pl-5">
              <b-button
                variant="link"
                v-if="!isDemo"
                @click="$emit('add-region-click')"
              >
                <b-icon icon="plus"></b-icon> Add Genomic Regions
              </b-button>
            </b-list-group-item>
            <b-list-group-item class="pl-5">
              <b-button
                variant="link"
                v-if="!isDemo"
                @click="$emit('add-metadata-click')"
              >
                <b-icon icon="tag-fill"></b-icon> Add Metadata
              </b-button>
              <b-button variant="link" v-if="isDemo">
                <b-icon icon="tag-fill"></b-icon> Add Metadata
                <b-tooltip target="deactivated-demo" placement="top"
                  >Deactivated in demo mode</b-tooltip
                >
              </b-button>
            </b-list-group-item>
            <b-list-group-item class="pl-5">
              <b-button
                variant="link"
                v-if="!isDemo"
                @click="$emit('preprocess-dataset-click')"
              >
                <b-icon icon="box-arrow-up-right"></b-icon> Preprocess Features
              </b-button>
              <b-button variant="link" v-if="isDemo">
                <b-icon icon="box-arrow-up-right"></b-icon> Preprocess Features
                <b-tooltip target="deactivated-demo" placement="top"
                  >Deactivated in demo mode</b-tooltip
                >
              </b-button>
            </b-list-group-item>
            <b-list-group-item class="pl-5">
              <b-button
                variant="link"
                v-if="!isDemo"
                @click="$emit('preprocess-collections-click')"
              >
                <b-icon icon="box-arrow-up-right"></b-icon> Preprocess Collections
              </b-button>
              <b-button variant="link" v-if="isDemo">
                <b-icon icon="box-arrow-up-right"></b-icon> Preprocess Collections
                <b-tooltip target="deactivated-demo" placement="top"
                  >Deactivated in demo mode</b-tooltip
                >
              </b-button>
            </b-list-group-item>
            <b-list-group-item class="pl-5">
              <b-button
                variant="link"
                @click="$emit('mydataset-click', 'bedfile')"
              >
                <b-icon icon="list-ul"></b-icon> Show Regions
              </b-button>
            </b-list-group-item>
          </b-list-group>
        </b-collapse>

      <b-list-group-item>
        <b-button
          variant="link"
          class="text-left w-100"
          v-b-toggle.collapse-features
        >
                    <b-icon icon="bar-chart-fill"></b-icon> Features
        </b-button>
      </b-list-group-item>
        
        <b-collapse id="collapse-features">
          <b-list-group flush>
            <b-list-group-item class="pl-5">
              <b-button
                variant="link"
                v-if="!isDemo"
                @click="$emit('add-feature-click')"
              >
                <b-icon icon="plus"></b-icon> Add Genomic Features
              </b-button>
              <b-button variant="link" v-if="isDemo">
                <b-icon icon="plus"></b-icon> Add Genomic Features
                <b-tooltip target="deactivated-demo" placement="top"
                  >Deactivated in demo mode</b-tooltip
                >
              </b-button>
            </b-list-group-item>
            <b-list-group-item class="pl-5">
              <b-button
                variant="link"
                @click="$emit('mydataset-click', 'features')"
              >
                <b-icon icon="list-ul"></b-icon> Show Features
              </b-button>
            </b-list-group-item>
          </b-list-group>
        </b-collapse>

    <b-list-group-item>
        <b-button
          variant="link"
          class="text-left w-100"
          v-b-toggle.collapse-collections
        >
          <b-icon icon="layers-fill"></b-icon> Collections
        </b-button>
    </b-list-group-item>

        <b-collapse id="collapse-collections">
          <b-list-group flush>
            <b-list-group-item class="pl-5">
              <b-button
                variant="link"
                v-if="!isDemo"
                @click="$emit('add-collection-click')"
              >
                <b-icon icon="plus"></b-icon> Create Dataset Collection
              </b-button>
              <b-button variant="link" v-if="isDemo">
                <b-icon icon="plus"></b-icon> Create Dataset Collection
                <b-tooltip target="deactivated-demo" placement="top"
                  >Deactivated in demo mode</b-tooltip
                >
              </b-button>
            </b-list-group-item>
            <b-list-group-item class="pl-5">
              <b-button
                variant="link"
                @click="$emit('show-collection-click')"
              >
                <b-icon icon="list-ul"></b-icon> Show Dataset Collections
              </b-button>
            </b-list-group-item>
          </b-list-group>
        </b-collapse>

      <b-list-group-item>
        <b-button
          variant="link"
          class="text-left w-100"
          v-b-toggle.collapse-genomes
        >
          <b-icon icon="circle-fill"></b-icon> Genomes
        </b-button>
      </b-list-group-item>


        <b-collapse id="collapse-genomes">
          <b-list-group flush>
            <b-list-group-item class="pl-5">
              <b-button
                variant="link"
                v-if="!isDemo"
                @click="$emit('add-assembly-click')"
              >
                <b-icon icon="plus"></b-icon> Add Genome Assembly
              </b-button>
              <b-button variant="link" v-if="isDemo">
                <b-icon icon="plus"></b-icon> Add Genome Assembly
                <b-tooltip target="deactivated-demo" placement="top"
                  >Deactivated in demo mode</b-tooltip
                >
              </b-button>
            </b-list-group-item>
            <b-list-group-item class="pl-5">
              <b-button
                variant="link"
                    @click="$emit('show-assembly-click')"
              >
                <b-icon icon="list-ul"></b-icon> Show Genomes
              </b-button>
            </b-list-group-item>
          </b-list-group>
        </b-collapse>
    </b-list-group>
  </div>
</template>

<script>
export default {
    name: "drawer",
    data: function() {
        return {
            isDemo: process.env.SHOWCASE
        };
    }
};
</script>
