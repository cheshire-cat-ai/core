<script setup lang="ts">
import { usePlugins } from '@stores/usePlugins'
import { storeToRefs } from 'pinia'
import { firstLetter } from '@utils/commons'

const store = usePlugins()
const { currentState: pluginsState } = storeToRefs(store)
</script>

<template>
  <div class="flex flex-col self-center gap-8 md:w-3/4">
    <div class="flex flex-col items-center justify-center col-span-2 gap-6 p-8 rounded-xl bg-base-300">
      <p class="text-3xl font-bold text-primary">Plugins</p>
      <p class="font-medium text-center">
        This page displays the list of active plugins on the <strong>Cheshire Cat</strong>. 
        In the next version of the project, users will be able to activate or disable individual plugins according to their needs, 
        allowing for greater customization of the user experience.
      </p>
    </div>
    <div v-if="pluginsState.loading" class="flex items-center justify-center grow">
      <div role="status"
        class="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] text-primary motion-reduce:animate-[spin_1.5s_linear_infinite]">
        <span class="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
      </div>
    </div>
    <div v-else-if="pluginsState.error" class="flex items-center justify-center grow">
      <div class="p-4 font-bold shadow-xl rounded-xl text-base-100 bg-error">
        Failed to fetch
      </div>
    </div>
    <div v-else v-for="item in pluginsState.data" :key="item.id" class="flex items-center gap-4 p-4 bg-base-200 rounded-xl">
      <div class="avatar placeholder">
        <div class="w-20 h-20 rounded-xl bg-gradient-to-b from-blue-500 to-primary text-primary">
          <span class="text-5xl font-bold leading-3">{{ firstLetter(item.name) }}</span>
        </div>
      </div>
      <div class="flex flex-col gap-2">
        <p class="text-xl font-bold">{{ item.name }}</p>
        <p>{{ item.description }}</p>
      </div>
    </div>
  </div>
</template>
