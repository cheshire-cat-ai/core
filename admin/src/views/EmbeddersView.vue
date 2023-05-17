<script setup lang="ts">
import { useEmbedderConfig } from '@stores/useEmbedderConfig'
import type { EmbedderConfigMetaData } from '@models/EmbedderConfig'
import type { JSONSettings } from '@models/JSONSchema'
import SelectBox from '@components/SelectBox.vue'

const storeEmbedder = useEmbedderConfig()
const { getAvailableEmbedders, getEmbedderSchema, getEmbedderSettings, setEmbedderSettings } = storeEmbedder
const { currentState: embedderState } = storeToRefs(storeEmbedder)

const selectEmbedder = ref<InstanceType<typeof SelectBox>>()
const currentSchema = ref<EmbedderConfigMetaData>()
const currentSettings = ref<JSONSettings>({})

const emit = defineEmits<{
	(e: 'close'): void
}>()

const updateProperties = (selected = currentSchema.value?.title) => {
	currentSchema.value = getEmbedderSchema(selected)
	currentSettings.value = getEmbedderSettings(selected)
	Object.values(currentSchema.value?.properties ?? {}).forEach(p => {
		if (!p.env_names) return
		if (!currentSettings.value[p.env_names[0]]) currentSettings.value[p.env_names[0]] = p.default
	})
}

const saveEmbedder = async () => {
	const embName = selectEmbedder.value?.selectedElement
	if (!embName?.value) return
	const res = await setEmbedderSettings(embName.value, currentSettings.value)
	if (res) emit('close')
}

watchDeep(embedderState, () => {
	updateProperties(selectEmbedder.value?.selectedElement.value)
}, { flush: 'post', immediate: true })
</script>

<template>
	<div class="flex grow flex-col gap-4">
		<div v-if="embedderState.loading" class="flex grow items-center justify-center">
			<div role="status"
				class="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] text-primary motion-reduce:animate-[spin_1.5s_linear_infinite]">
				<span
					class="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
			</div>
		</div>
		<div v-else-if="embedderState.error || !getAvailableEmbedders().length"
			class="flex grow items-center justify-center">
			<div class="rounded bg-error p-4 font-bold text-base-100 shadow-xl">
				Failed to fetch
			</div>
		</div>
		<div v-else class="flex grow flex-col gap-4">
			<SelectBox ref="selectEmbedder" :picked="embedderState.selected"
				:list="getAvailableEmbedders().map(p => ({ label: p.name_human_readable, value: p.title }))"
				@update="e => updateProperties(e.value)" />
			<div class="flex flex-col gap-4">
				<div class="flex flex-col">
					<p class="text-sm text-neutral-focus">
						{{ currentSchema?.title }}
					</p>
					<p>{{ currentSchema?.description }}</p>
				</div>
				<div v-for="prop in currentSchema?.properties" :key="prop.title" class="flex flex-col gap-2">
					<p class="text-sm text-neutral-focus">
						<span v-if="!prop.default" class="font-bold text-error">*</span>
						{{ prop.title }}
					</p>
					<input v-model="currentSettings[prop.env_names![0]]" type="text" :placeholder="prop.title"
						class="input-bordered input-primary input input-sm w-full">
				</div>
			</div>
			<button class="btn-success btn-sm btn mt-auto normal-case" @click="saveEmbedder">
				Save
			</button>
		</div>
	</div>
</template>
