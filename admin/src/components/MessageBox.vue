<script setup lang="ts">
import hljs from 'highlight.js'
import { Remarkable } from 'remarkable'
import { linkify } from 'remarkable/linkify'
import 'highlight.js/styles/github.css'
import { useSettings } from '@stores/useSettings'
import SidePanel from '@components/SidePanel.vue'
import { JsonTreeView } from 'json-tree-view-vue3'

const { isDark } = storeToRefs(useSettings())

const whyPanel = ref<InstanceType<typeof SidePanel>>()

const markdown = new Remarkable({
    breaks: true,
    typographer: true,
    highlight: (str, lang) => {
        if (lang && hljs.getLanguage(lang)) {
            try { return hljs.highlight(str, { language: lang }).value } 
            catch (_) { console.log(_) }
        }
        try { return hljs.highlightAuto(str).value } 
        catch (_) { console.log(_) }
        return ''
    }
}).use(linkify)
markdown.inline.ruler.enable(['sup', 'sub'])
markdown.core.ruler.enable(['abbr'])
markdown.block.ruler.enable(['footnote', 'deflist'])

const props = defineProps<{
    sender: 'bot' | 'user',
    text: string,
    why: string
}>()

const cleanedText = props.text.replace(/"(.+)"/gm, '$1')
</script>

<template>
	<div class="chat gap-x-2" :class="[sender === 'bot' ? 'chat-start' : 'chat-end']">
		<div class="chat-image px-2">
			{{ sender === 'bot' ? '😺' : '🙂' }}
		</div>
		<div class="chat-bubble min-h-fit break-words rounded-md" :class="{'pr-8': why}">
			<p v-html="markdown.render(cleanedText)" />
			<button v-if="why" class="btn-info btn-square btn-xs btn absolute right-1 top-1 !p-0"
				@click="whyPanel?.togglePanel()">
				<p class="text-base text-neutral">
					?
				</p>
			</button>
		</div>
		<SidePanel ref="whyPanel" title="Why this response">
			<JsonTreeView :data="why" rootKey="why" :colorScheme="isDark ? 'dark' : 'light'" />
		</SidePanel>
	</div>
</template>

<style lang="scss">
.json-view-item.root-item .value-key {
    white-space: normal !important;
}
</style>
