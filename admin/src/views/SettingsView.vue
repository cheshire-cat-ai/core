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

const updateSelect = (element: any) => {
  currentSchema.value = getProviderSchema(element.value)
  currentSettings.value = getProviderSettings(element.value)
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
  <div class="grid self-center gap-8 md:grid-cols-2 md:w-3/4 place-items-stretch auto-rows-min">
    <div class="flex flex-col items-center justify-center gap-6 p-8 md:col-span-2 rounded-xl bg-base-300">
      <p class="text-3xl font-bold text-primary">Set up your Cat</p>
      <p class="font-medium">Configure your Cheshire Cat to suit your needs</p>
    </div>
    <div class="flex flex-col items-center justify-between gap-8 p-4 rounded-xl bg-base-200">
      <p class="text-xl font-medium text-primary">Language Model</p>
      <p class="text-center">Choose and configure your favourite Large Language Model</p>
      <button class="btn btn-sm btn-primary" @click="openSidePanel(1, 'Configure the Language Model')">Configure</button>
    </div>
    <div class="flex flex-col items-center justify-between gap-8 p-4 rounded-xl bg-base-200">
      <p class="text-xl font-medium text-primary">Embedder</p>
      <p class="text-center">Choose a language embedder to help the Cat remember conversations and documents</p>
      <button class="btn btn-sm btn-primary" disabled @click="openSidePanel(2, 'Configure the Embedder')">Configure</button>
    </div>
    <div class="flex items-center justify-center md:col-span-2">
      <p class="font-semibold">
        Admin UI made by 
        <a class="cursor-pointer text-primary" target="_blank" 
          href="https://github.com/zAlweNy26/vue-cheshire-cat">zAlweNy26</a>
      </p>
    </div>
    <SidePanel ref="sidePanel" :title="sidePanelTitle">
      <div v-if="llmState.loading" class="flex items-center justify-center grow">
        <div role="status"
          class="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] text-primary motion-reduce:animate-[spin_1.5s_linear_infinite]">
          <span class="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
        </div>
      </div>
      <div v-else-if="llmState.error" class="flex items-center justify-center grow">
        <div class="p-4 font-bold shadow-xl rounded-xl text-base-100 bg-error">
          Failed to fetch
        </div>
      </div>
      <div v-else-if="sidePanelContent === 1 && getAvailableProviders().length" class="flex flex-col gap-4 grow">
        <SelectBox ref="selectProvider" :selected="llmState.selected"
          :list="getAvailableProviders().map(p => ({ label: p.name_human_readable, value: p.languageModelName }))" 
          @update="updateSelect"
        />
        <div class="flex flex-col gap-2">
          <p class="text-sm text-neutral-focus">{{ currentSchema?.title }}</p>
          <p>{{ currentSchema?.description }}</p>
          <template v-for="prop in currentSchema?.properties">
            <p class="text-sm text-neutral-focus">
              <span v-if="!prop.default" class="text-error">*</span>
              {{ prop.title }}
            </p>
            <input type="text" v-model="currentSettings[prop.env_names![0]]"
              :placeholder="prop.title" class="w-full input-primary input input-sm input-bordered" />
          </template>
        </div>
        <button class="mt-auto normal-case btn btn-sm btn-success" @click="saveProvider">Save</button>
      </div>
      <div v-else-if="sidePanelContent === 2">
        Work In Progress - Embedder
      </div>
    </SidePanel>
  </div>
</template>
