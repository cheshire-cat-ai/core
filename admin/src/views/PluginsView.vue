<script setup lang="ts">
import { usePlugins } from '@stores/usePlugins'
import { firstLetter } from '@utils/commons'

const store = usePlugins()
const { togglePlugin } = store
const { currentState: pluginsState } = storeToRefs(store)
</script>

<template>
	<div class="flex flex-col gap-8 self-center md:w-3/4">
		<div class="col-span-2 flex flex-col items-center justify-center gap-3 rounded p-6">
			<p class="text-3xl font-bold text-primary">
				Plugins
			</p>
			<p class="text-center font-medium">
				This page displays the list of active plugins on the <strong>Cheshire Cat</strong>. 
				In the next version of the project, users will be able to activate or disable individual plugins according to their needs, 
				allowing for greater customization of the user experience.
			</p>
		</div>
		<div v-if="pluginsState.loading" class="flex grow items-center justify-center">
			<div role="status"
				class="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] text-primary motion-reduce:animate-[spin_1.5s_linear_infinite]">
				<span class="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
			</div>
		</div>
		<div v-else-if="pluginsState.error" class="flex grow items-center justify-center">
			<div class="rounded bg-error p-4 font-bold text-base-100 shadow-xl">
				Failed to fetch
			</div>
		</div>
		<template v-else>
			<div v-for="item in pluginsState.data" :key="item.id" class="flex items-center gap-4 rounded bg-base-200 p-4">
				<div class="placeholder avatar">
					<div class="h-20 w-20 rounded bg-gradient-to-b from-blue-500 to-primary text-base-100">
						<span class="text-5xl font-bold leading-3">{{ firstLetter(item.name) }}</span>
					</div>
				</div>
				<div class="flex flex-col gap-2">
					<p class="flex flex-wrap justify-between text-xl font-bold">
						<span>{{ item.name }}</span>
						<input type="checkbox" class="!toggle !toggle-success" @click="togglePlugin(item.id)">
					</p>
					<p>{{ item.description }}</p>
				</div>
			</div>
		</template>
	</div>
</template>
