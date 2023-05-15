<script setup lang="ts">
import hljs from 'highlight.js'
import { Remarkable } from 'remarkable'
import { linkify } from 'remarkable/linkify'
import 'highlight.js/styles/github.css'

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
    text: string
}>()

const cleanedText = props.text.replace(/"(.+)"/gm, '$1')
</script>

<template>
	<div class="chat gap-y-2" :class="[sender === 'bot' ? 'chat-start' : 'chat-end']">
		<div class="chat-image px-2">
			{{ sender === 'bot' ? '😺' : '🙂' }}
        </div>
		<div class="chat-bubble rounded-md min-h-fit break-words" v-html="markdown.render(cleanedText)" />
	</div>
</template>
