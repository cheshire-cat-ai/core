<script setup lang="ts">
import { ref, watchEffect } from 'vue'
import SidePanel from '@components/SidePanel.vue'
import SelectBox from '@components/SelectBox.vue'
import { useLLMProviders } from '@stores/useLLMProviders'
import { storeToRefs } from 'pinia'
import type { LLMProviderMetaData, LLMSettings } from '@models/LLMProvider'

const store = useLLMProviders()
const { getAvailableProviders, getProviderSchema, setLLMSettings, getProviderSettings } = store
const { currentState: llmState } = storeToRefs(store)

const sidePanel = ref<InstanceType<typeof SidePanel>>()
const selectProvider = ref<InstanceType<typeof SelectBox>>()
const sidePanelTitle = ref(""), sidePanelContent = ref(0)
const currentSchema = ref<LLMProviderMetaData>()
const currentSettings = ref<LLMSettings>({})

watchEffect(() => {
	if (!llmState.value.loading && sidePanel.value?.open) {
		currentSchema.value = getProviderSchema() ?? getAvailableProviders()[0]
		currentSettings.value = getProviderSettings()
	}
})

const saveProvider = async () => {
	const llmName = selectProvider.value?.selectedElement
	if (!llmName?.value) return
	const res = await setLLMSettings(llmName.value, currentSettings.value)
	if (res) sidePanel.value?.togglePanel()
}

const updateProperties = (selectedLLM: string) => {
	currentSchema.value = getProviderSchema(selectedLLM)
	currentSettings.value = getProviderSettings(selectedLLM)
	Object.values(currentSchema.value?.properties ?? {}).forEach(p => {
		if (!p.env_names) return
		if (!currentSettings.value[p.env_names[0]]) currentSettings.value[p.env_names[0]] = p.default
	})
}

const openSidePanel = (content: number, title: string) => {
	sidePanelContent.value = content
	sidePanelTitle.value = title
	sidePanel.value?.togglePanel()
}
</script>

<template>
	<div class="grid self-center gap-8 auto-rows-min place-items-stretch md:w-3/4 md:grid-cols-2">
		<div class="flex flex-col items-center justify-center gap-6 p-8 rounded-xl bg-base-300 md:col-span-2">
			<p class="text-3xl font-bold text-primary">
				Set up your Cat
			</p>
			<p class="font-medium">
				Configure your Cheshire Cat to suit your needs
			</p>
		</div>
		<div class="flex flex-col items-center justify-between gap-8 p-4 rounded-xl bg-base-200">
			<p class="text-xl font-medium text-primary">
				Language Model
			</p>
			<p class="text-center">
				Choose and configure your favourite Large Language Model
			</p>
			<button class="btn-primary btn-sm btn" @click="openSidePanel(1, 'Configure the Language Model')">
				Configure
			</button>
		</div>
		<div class="flex flex-col items-center justify-between gap-8 p-4 rounded-xl bg-base-200">
			<p class="text-xl font-medium text-primary">
				Embedder
			</p>
			<p class="text-center">
				Choose a language embedder to help the Cat remember conversations and documents
			</p>
			<button class="btn-primary btn-sm btn" disabled @click="openSidePanel(2, 'Configure the Embedder')">
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
			<div v-if="llmState.loading" class="flex items-center justify-center grow">
				<div role="status"
					class="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] text-primary motion-reduce:animate-[spin_1.5s_linear_infinite]">
					<span
						class="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
				</div>
			</div>
			<div v-else-if="llmState.error" class="flex items-center justify-center grow">
				<div class="p-4 font-bold shadow-xl rounded-xl bg-error text-base-100">
					Failed to fetch
				</div>
			</div>
			<div v-else-if="sidePanelContent === 1 && getAvailableProviders().length" class="flex flex-col gap-4 grow">
				<SelectBox ref="selectProvider" :picked="llmState.selected"
					:list="getAvailableProviders().map(p => ({ label: p.name_human_readable, value: p.languageModelName }))"
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
							class="w-full input-bordered input-primary input input-sm">
					</template>
				</div>
				<button class="mt-auto normal-case btn-success btn-sm btn" @click="saveProvider">
					Save
				</button>
			</div>
			<div v-else-if="sidePanelContent === 2">
				Work In Progress - Embedder
			</div>
		</SidePanel>
	</div>
</template>
