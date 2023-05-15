<script setup lang="ts">
import SidePanel from '@components/SidePanel.vue'

const panelTitles = [ 'Configure the Language Model', 'Configure the Embedder' ] as const

const sidePanel = ref<InstanceType<typeof SidePanel>>()
const panelTitle = ref<string>('')

const openSidePanel = (title: typeof panelTitles[number]) => {
	panelTitle.value = title
	sidePanel.value?.togglePanel()
}
</script>

<template>
	<div class="grid auto-rows-min place-items-stretch gap-8 self-center md:w-3/4 md:grid-cols-2">
		<div class="flex flex-col items-center justify-center gap-6 rounded bg-base-300 p-8 md:col-span-2">
			<p class="text-2xl text-primary">
				Set up your Cat
			</p>
			<p class="font-medium">
				Configure your Cheshire Cat to suit your needs
			</p>
		</div>
		<div class="flex flex-col items-center justify-between gap-8 rounded bg-base-200 p-4">
			<p class="text-xl text-primary">
				Language Model
			</p>
			<p class="text-center">
				Choose and configure your favourite Large Language Model
			</p>
			<RouterLink :to="{ name: 'providers' }" class="btn-primary btn-sm btn"
				@click="openSidePanel('Configure the Language Model')">
				Configure
			</RouterLink>
		</div>
		<div class="flex flex-col items-center justify-between gap-8 rounded bg-base-200 p-4">
			<p class="text-xl text-primary">
				Embedder
			</p>
			<p class="text-center">
				Choose a language embedder to help the Cat remember conversations and documents
			</p>
			<RouterLink :to="{ name: 'embedders' }" class="btn-primary btn-sm btn" 
				@click="openSidePanel('Configure the Embedder')">
				Configure
			</RouterLink>
		</div>
		<SidePanel ref="sidePanel" :title="panelTitle">
			<RouterView @close="sidePanel?.togglePanel()" />
		</SidePanel>
	</div>
</template>
