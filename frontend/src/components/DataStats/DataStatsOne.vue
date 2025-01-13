<template>
  <div class="cards-container">
    <!-- Card Item Start -->
    <transition-group
      name="card-move"
      tag="div"
      class="d-flex justify-content-start flex-row gap-4"
    >
      <div
        v-for="(item, index) in cardItems"
        :key="item.id"
        class="card-item rounded-sm border border-stroke bg-white py-6 px-30 shadow-default dark:border-strokedark dark:bg-boxdark"
        draggable="true"
        @dragstart="startDrag(index)"
        @dragover.prevent
        @drop="onDrop(index)"
      >
        <!-- <div
          class="flex h-11.5 w-11.5 items-center justify-center rounded-full bg-meta-2 dark:bg-meta-4"
          v-html="item.icon"
        ></div> -->

        <!-- <div class="mt-4 d-flex items-end justify-between">
          <div>
            <h4 class="text-title-md font-bold text-black dark:text-white">
              {{ item.title }}
            </h4>
            <span class="text-sm font-medium">{{ item.total }}</span>
          </div>

          <span
            class="flex items-center gap-1 text-sm font-medium"
            :class="{
              'text-meta-3': item.growthRate > 0,
              'text-meta-5': item.growthRate < 0,
            }"
          >
            {{ item.growthRate }}%
            <svg
              v-if="item.growthRate > 0"
              class="fill-meta-3"
              width="10"
              height="11"
              viewBox="0 0 10 11"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M4.35716 2.47737L0.908974 5.82987L5.0443e-07 4.94612L5 0.0848689L10 4.94612L9.09103 5.82987L5.64284 2.47737L5.64284 10.0849L4.35716 10.0849L4.35716 2.47737Z"
                fill=""
              />
            </svg>

            <svg
              v-if="item.growthRate < 0"
              class="fill-meta-5"
              width="10"
              height="11"
              viewBox="0 0 10 11"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M5.64284 7.69237L9.09102 4.33987L10 5.22362L5 10.0849L-8.98488e-07 5.22362L0.908973 4.33987L4.35716 7.69237L4.35716 0.0848701L5.64284 0.0848704L5.64284 7.69237Z"
                fill=""
              />
            </svg>
          </span>
        </div> -->
      </div>
    </transition-group>
    <!-- Card Item End -->
  </div>
</template>

<script>
export default {
  data() {
    return {
      cardItems: [
        {
          id: 1,
          icon: "📈", // Replace with your SVG/icon
          total: "100",
          title: "S&P 500",
          growthRate: 5,
        },
        {
          id: 2,
          icon: "📈",
          total: "200",
          title: "Nasdaq",
          growthRate: -3,
        },
        {
          id: 3,
          icon: "📈",
          total: "300",
          title: "Dow Jones",
          growthRate: 10,
        },
        {
          id: 4,
          icon: "📈",
          total: "400",
          title: "Russell 2000",
          growthRate: 10,
        },
      ],
      draggedItemIndex: null,
    };
  },
  methods: {
    startDrag(index) {
      this.draggedItemIndex = index;
    },
    onDrop(index) {
      if (this.draggedItemIndex !== null) {
        const draggedItem = this.cardItems[this.draggedItemIndex];
        this.cardItems.splice(this.draggedItemIndex, 1);
        this.cardItems.splice(index, 0, draggedItem);
        this.draggedItemIndex = null;
      }
    },
  },
};
</script>

<style>
.cards-container {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.card-item {
  transition: transform 0.3s ease-in-out;
}

.card-move-enter-active,
.card-move-leave-active {
  transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
}

.card-move-enter,
.card-move-leave-to {
  transform: translateY(20px);
  opacity: 0;
}
</style>
