<script setup lang="ts">
import SidePanel from '@components/SidePanel.vue'
import SelectBox from '@components/SelectBox.vue'
import { useLLMProviders } from '@stores/useLLMProviders'
import { useEmbedders } from '@stores/useEmbedders'
import type { LLMProviderMetaData } from '@models/LLMProvider'
import type { JSONSettings } from '@models/JSONSchema'
import type { EmbedderMetaData } from '@models/Embedder'

const storeProviders = useLLMProviders()
const { getAvailableProviders, getProviderSchema, setLLMSettings, getProviderSettings } = storeProviders
const { currentState: llmState } = storeToRefs(storeProviders)

const storeEmbedders = useEmbedders()
const { getAvailableEmbedders, getEmbedderSchema, getEmbedderSettings } = storeEmbedders
const { currentState: embedderState } = storeToRefs(storeEmbedders)

const panelTitles = [ 'Configure the Language Model', 'Configure the Embedder' ] as const
type PanelTitle = typeof panelTitles[number] | ''

const sidePanel = ref<InstanceType<typeof SidePanel>>()
const selectProvider = ref<InstanceType<typeof SelectBox>>(), selectEmbedder = ref<InstanceType<typeof SelectBox>>()
const sidePanelTitle = ref<PanelTitle>('')
const currentSchema = ref<LLMProviderMetaData | EmbedderMetaData>()
const currentSettings = ref<JSONSettings>({})

const saveProvider = async () => {
	const llmName = selectProvider.value?.selectedElement
	if (!llmName?.value) return
	const res = await setLLMSettings(llmName.value, currentSettings.value)
	if (res) sidePanel.value?.togglePanel()
}

const updateProperties = (selected: string) => {
	currentSchema.value = sidePanelTitle.value === 'Configure the Embedder' ? getEmbedderSchema(selected) : getProviderSchema(selected)
	currentSettings.value = sidePanelTitle.value === 'Configure the Embedder' ? getEmbedderSettings(selected) : getProviderSettings(selected)
	Object.values(currentSchema.value?.properties ?? {}).forEach(p => {
		if (!p.env_names) return
		if (!currentSettings.value[p.env_names[0]]) currentSettings.value[p.env_names[0]] = p.default
	})
}

const openSidePanel = (title: PanelTitle) => {
	sidePanelTitle.value = title
	if (title === 'Configure the Language Model') {
		currentSchema.value = getProviderSchema() ?? getAvailableProviders()[0]
		currentSettings.value = getProviderSettings()
		updateProperties(currentSchema.value.title)
	} else if (title === 'Configure the Embedder') {
		currentSchema.value = getEmbedderSchema() ?? getAvailableEmbedders()[0]
		currentSettings.value = getEmbedderSettings()
		updateProperties(currentSchema.value.title)
	}
	sidePanel.value?.togglePanel()	
}
</script>

<template>
	<div class="grid auto-rows-min place-items-stretch gap-8 self-center md:w-3/4 md:grid-cols-2">
		<div class="flex flex-col items-center justify-center gap-6 rounded-xl bg-base-300 p-8 md:col-span-2">
			<p class="text-3xl font-bold text-primary">
				Set up your Cat
			</p>
			<p class="font-medium">
				Configure your Cheshire Cat to suit your needs
			</p>
		</div>
		<div class="flex flex-col items-center justify-between gap-8 rounded-xl bg-base-200 p-4">
			<p class="text-xl font-medium text-primary">
				Language Model
			</p>
			<p class="text-center">
				Choose and configure your favourite Large Language Model
			</p>
			<button class="btn-primary btn-sm btn" @click="openSidePanel('Configure the Language Model')">
				Configure
			</button>
		</div>
		<div class="flex flex-col items-center justify-between gap-8 rounded-xl bg-base-200 p-4">
			<p class="text-xl font-medium text-primary">
				Embedder
			</p>
			<p class="text-center">
				Choose a language embedder to help the Cat remember conversations and documents
			</p>
			<button class="btn-primary btn-sm btn" @click="openSidePanel('Configure the Embedder')">
				Configure
			</button>
		</div>
		<div class="flex items-center justify-center md:col-span-2">
			<p class="font-semibold">
				Admin UI made by
				<a class="cursor-pointer text-primary" target="_blank"
					href="https://github.com/zAlweNy26">zAlweNy26</a>
			</p>
		</div>
		<SidePanel ref="sidePanel" :title="sidePanelTitle">
			<div v-if="sidePanelTitle === 'Configure the Language Model'" 
				class="flex grow flex-col gap-4">
				<div v-if="llmState.loading" class="flex grow items-center justify-center">
					<div role="status"
						class="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] text-primary motion-reduce:animate-[spin_1.5s_linear_infinite]">
						<span
							class="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
					</div>
				</div>
				<div v-else-if="llmState.error || !getAvailableProviders().length" class="flex grow items-center justify-center">
					<div class="rounded-xl bg-error p-4 font-bold text-base-100 shadow-xl">
						Failed to fetch
					</div>
				</div>
				<div v-else class="flex grow flex-col gap-4">
					<SelectBox ref="selectProvider" :picked="llmState.selected"
						:list="getAvailableProviders().map(p => ({ label: p.name_human_readable, value: p.title }))"
						@update="e => updateProperties(e.value)" />
					<div class="flex flex-col gap-2">
						<p class="text-sm text-neutral-focus">
							{{ currentSchema?.title }}
						</p>
						<p>{{ currentSchema?.description }}</p>
						<template v-for="prop in currentSchema?.properties" :key="prop.title">
							<p class="text-sm text-neutral-focus">
								<span v-if="!prop.default" class="text-error">*</span>
								{{ prop.title }}
							</p>
							<input v-model="currentSettings[prop.env_names![0]]" type="text" :placeholder="prop.title"
								class="input-bordered input-primary input input-sm w-full">
						</template>
					</div>
					<button class="btn-success btn-sm btn mt-auto normal-case" @click="saveProvider">
						Save
					</button>
				</div>
			</div>
			<div v-else-if="sidePanelTitle === 'Configure the Embedder'" class="flex grow flex-col gap-4">
				<div v-if="embedderState.loading" class="flex grow items-center justify-center">
					<div role="status"
						class="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] text-primary motion-reduce:animate-[spin_1.5s_linear_infinite]">
						<span
							class="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
					</div>
				</div>
				<div v-else-if="embedderState.error || !getAvailableEmbedders().length" class="flex grow items-center justify-center">
					<div class="rounded-xl bg-error p-4 font-bold text-base-100 shadow-xl">
						Failed to fetch
					</div>
				</div>
				<div v-else class="flex grow flex-col gap-4">
					<SelectBox ref="selectEmbedder" :picked="embedderState.selected"
						:list="getAvailableEmbedders().map(p => ({ label: p.name_human_readable, value: p.title }))"
						@update="e => updateProperties(e.value)" />
					<div class="flex flex-col gap-2">
						<p class="text-sm text-neutral-focus">
							{{ currentSchema?.title }}
						</p>
						<p>{{ currentSchema?.description }}</p>
						<template v-for="prop in currentSchema?.properties" :key="prop.title">
							<p class="text-sm text-neutral-focus">
								<span v-if="!prop.default" class="text-error">*</span>
								{{ prop.title }}
							</p>
							<input v-model="currentSettings[prop.env_names![0]]" type="text" :placeholder="prop.title"
								class="input-bordered input-primary input input-sm w-full">
						</template>
					</div>
				</div>
			</div>
		</SidePanel>
	</div>
</template>
