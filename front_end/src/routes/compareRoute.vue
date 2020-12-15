<template>
<div>
  <div id="dropZone1" class="halfheight"  @drop='onDrop($event, 1)' @dragover.prevent @dragenter.prevent>
    <div class="inline" v-for="item in listOne" :key="item.id" draggable @dragstart="startDrag($event, item)" @drop="dropFuse($event, item)" @dragover.prevent @dragenter.prevent>
      <md-card md-with-hover :style="item.class">
              <md-card-header>
                  <md-button class="md-icon-button" @click="splitItems(item)" v-if="item.children.length != 0">
                      <md-icon>dashboard</md-icon>
                  </md-button>
                  <div class="md-title">{{ item.header }}</div>
              </md-card-header>

              <md-card-content>
                    <md-empty-state>
                      I am in list 1!
                    </md-empty-state>
              </md-card-content>
      </md-card>
    </div>
  </div>
  <div id="dropZone2" class="halfheight" @drop='onDrop($event, 2)' @dragover.prevent @dragenter.prevent>
      <div class="inline" v-for="item in listTwo" :key="item.id" draggable @dragstart="startDrag($event, item)" @drop="dropFuse($event, item)" @dragover.prevent @dragenter.prevent>
        <md-card md-with-hover :style="item.class">
                <md-card-header>
                    <div class="md-title">{{ item.header }}</div>
                    <md-button class="md-icon-button" @click="splitItems(item)" v-if="item.children.length != 0">
                      <md-icon>dashboard</md-icon>
                    </md-button>
                </md-card-header>

                <md-card-content>
                    <md-empty-state>
                      I am in list 2!
                    </md-empty-state>
                </md-card-content>
          </md-card>
      </div>
    </div>
</div>
</template>

<script>
  export default {
    name: 'EmptyStateRounded',
    data: function () {
      return {
        items : [{
          id: 1,
          header:"Example1",
          list: 1,
          children: [],
          class: {
            width: "30vw",
            height: "20vh"
          }
        },
        {
          id: 2,
          header:"Example2",
          list: 1,
          children: [],
          class: {
            width: "30vw",
            height: "20vh"
          }
        },
        {
          id: 3,
          header:"Example3",
          list: 1,
          children: [],
          class: {
            width: "30vw",
            height: "20vh"
          }
        }
        ]
      }
    },
    computed: {
      listOne: function () {
        return this.items.filter((element) => element.list == 1);
      },
      listTwo: function () {
        return this.items.filter((element) => element.list == 2);
      }
    },
    methods: {
      viewportWidthToPx(viewportString){
          const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
          var viewPortFraction = Number(viewportString.split("vw")[0]) / 100;
          return vw * viewPortFraction;
          
      },
      viewportHeightToPx(viewportString){
          const vh = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0);
          var viewPortFraction = Number(viewportString.split("vh")[0]) / 100;
          return vh * viewPortFraction;
          
      },
      splitItems(item){
        var thisItem = this.items.find(element => element.id == item.id);
        thisItem.class.height = "20vh";
        thisItem.class.width = "30vw"
        thisItem.header = thisItem.header.split(" ")[0];
        for (var toAppend of thisItem.children){
          var checkItem = this.items.find(element => element.id == toAppend.id);
          if (!checkItem){
            this.items.push(toAppend);
          }
        }
        thisItem.children = [];
      },
      dropFuse (evt, item) {
        const gettingDropped = evt.dataTransfer.getData('itemID');
        var gettingDroppedItem = this.items.find(element => element.id == gettingDropped);
        if (gettingDropped == item.id){
          return
        }
        const receivingItem =  this.items.find(element => element.id == item.id);
        receivingItem.header = receivingItem.header + " " + gettingDroppedItem.header
        // 
        // check whether width or height should be fixed
        var currentwidth = this.viewportWidthToPx(receivingItem.class.width)
        var currentheight = this.viewportHeightToPx(receivingItem.class.height)
        var droppedOffsetX = evt.offsetX;
        var droppedOffsetY = evt.offsetY;
        if ( (droppedOffsetX < currentwidth/2) && (droppedOffsetY > currentheight/2)){
            var currentHeight = Number(receivingItem.class.height.split("vh")[0]);
            var newHeight = currentHeight + 20;
            receivingItem.class.height = `${newHeight}vh`;
        }else{
            var currentWidth = Number(receivingItem.class.width.split("vw")[0]);
            var newWidth = currentWidth + 30;
            receivingItem.class.width = `${newWidth}vw`;
        }
        // check whether dropped item is in children
        var searchedItem = receivingItem.children.find(element => element.id == gettingDropped);
        if (!searchedItem){
          receivingItem.children.push(gettingDroppedItem);
          this.items = this.items.filter((element) => element.id != gettingDropped);
        }
      },
      startDrag: (evt, item) => {
            evt.dataTransfer.dropEffect = 'move'
            evt.dataTransfer.effectAllowed = 'move'
            evt.dataTransfer.setData('itemID', item.id)
            },
      onDrop (evt, list) {
            const itemID = evt.dataTransfer.getData('itemID');
            const item = this.items.find(item => item.id == itemID)
            if (item){
              item.list = list
            }
      }
    }
  }
</script>

<style scoped>

.inline {
  display: inline-block;
}

.halfheight {
  height: 40vh;
}

.drag-el {
  background-color: #fff;
  margin-bottom: 10px;
  padding: 5px;
}


</style>