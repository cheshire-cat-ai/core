<script setup lang="ts">
import { useRabbitHole } from '@stores/useRabbitHole'
import { useMessages } from '@stores/useMessages'
import { useSpeechRecognition, watchDeep, useFileDialog } from '@vueuse/core'
import { storeToRefs } from 'pinia'
import { computed, watchEffect, ref } from 'vue'
import { useSound } from '@vueuse/sound'
import { AcceptedContentTypes } from '@services/RabbitHole'
import { useSettings } from '@stores/useSettings'

const messagesStore = useMessages()
const { dispatchMessage, selectRandomDefaultMessages } = messagesStore
const { currentState: messagesState } = storeToRefs(messagesStore)

const textArea = ref<HTMLElement | null>(null)
const userMessage = ref(''), isTwoLines = ref(false)
const { isListening, isSupported, start: startRecording, stop: stopRecording, result: transcript } = useSpeechRecognition()
const { files, open: openFile } = useFileDialog()
const { play: playPop } = useSound('pop.mp3')
const { play: playRec } = useSound('start-rec.mp3')

const filesStore = useRabbitHole()
const { sendFile } = filesStore
const { currentState: rabbitHoleState } = storeToRefs(filesStore)

const { isAudioEnabled } = storeToRefs(useSettings())

const inputDisabled = computed(() => {
	return messagesState.value.loading || isListening.value || 
		!messagesState.value.ready || Boolean(messagesState.value.error)
})

const randomDefaultMessages = selectRandomDefaultMessages()

/**
 * When the user stops recording, the transcript will be sent to the messages service
 */
watchEffect(() => {
	if (isListening.value && isAudioEnabled.value) playRec()
	if (transcript.value === '') return
	dispatchMessage(transcript.value)
})

/**
 * Checks if the textarea needs to be multiline and updates the state accordingly.
 */
watchEffect(() => {
	if (textArea.value == null || !userMessage.value) {
		isTwoLines.value = false
		return
	}
	const letterWidth = 7.95
	const isMultiLine = letterWidth * userMessage.value.length > textArea.value.offsetWidth
	const hasLineBreak = !!(/\r|\n/.exec(userMessage.value))
	isTwoLines.value = (textArea.value && !userMessage.value) || (isMultiLine || hasLineBreak)
})

/**
 * Handles the file upload change by calling the onUpload callback if it exists.
 */
watchEffect(() => {
	if (files.value === null) return
	sendFile(files.value[0])
})

/**
 * When a new message arrives and audio is enabled, a pop sound will be played
 */
watchDeep(messagesState, () => {
	scrollToBottom()
	if (messagesState.value.messages.length > 0 && isAudioEnabled.value) {
		playPop()
	}
})

/**
 * Dispatches the user's message to the service.
 */
const sendMessage = (message: string) => {
	if (message === '') return
	userMessage.value = ''
	dispatchMessage(message)
}

const preventSend = (e: KeyboardEvent) => {
	if (e.key === 'Enter' && !e.shiftKey) {
		e.preventDefault()
		sendMessage(userMessage.value)
	}
}

const generatePlaceholder = (isLoading: boolean, isRecording: boolean, error?: string) => {
	if (error) return 'Well, well, well, looks like something has gone amiss'
	if (isLoading) return 'The enigmatic Cheshire cat is pondering...'
	if (isRecording) return 'The curious Cheshire cat is all ear...'
	return 'Ask the Cheshire Cat...'
}

const scrollToBottom = () => window.scrollTo({ behavior: 'smooth', left: 0, top: document.body.scrollHeight })
</script>

<template>
	<div class="flex w-full max-w-screen-lg flex-col justify-center gap-4 self-center overflow-hidden pb-16 md:!pb-20">
		<div v-if="!messagesState.ready" class="flex grow items-center justify-center self-center">
			<p v-if="messagesState.error" class="w-fit rounded-xl bg-error p-4 font-semibold text-base-100">
				{{ messagesState.error }}
			</p>
			<p v-else>
				Getting ready...
			</p>
		</div>
		<div v-else-if="messagesState.messages.length" class="flex grow flex-col overflow-y-auto">
			<MessageBox v-for="msg in messagesState.messages" :key="msg.id" :sender="msg.sender" :text="msg.text" />
			<p v-if="messagesState.error" class="w-fit rounded-xl bg-error p-4 font-semibold">
				{{ messagesState.error }}
			</p>
			<p v-else-if="!messagesState.error && messagesState.loading">
				😺 Cheshire cat is thinking...
			</p>
		</div>
		<div v-else class="flex grow cursor-pointer flex-col items-center justify-center gap-4">
			<div v-for="(msg, index) in randomDefaultMessages" :key="index" class="btn rounded-full normal-case shadow-xl"
				@click="sendMessage(msg)">
				{{ msg }}
			</div>
		</div>
		<div class="fixed bottom-0 left-0 flex w-full items-center justify-center bg-gradient-to-t from-base-100 p-2 md:p-4">
			<div class="flex w-full max-w-screen-lg items-center gap-2 md:gap-4">
				<label class="swap btn-circle btn border-none bg-transparent text-primary hover:bg-base-300">
					<input v-model="isAudioEnabled" type="checkbox" class="modal-toggle">
					<akar-icons-sound-on class="swap-on h-6 w-6" />
					<akar-icons-sound-off class="swap-off h-6 w-6" />
				</label>
				<div class="relative w-full">
					<textarea ref="textArea" v-model="userMessage" :rows="isTwoLines ? '2' : '1'" :disabled="inputDisabled"
						class="textarea-bordered textarea block w-full resize-none overflow-hidden pr-24 !outline-none !ring-0 focus:border-2 focus:border-primary"
						:placeholder="generatePlaceholder(messagesState.loading, isListening, messagesState.error)"
						@keydown="preventSend" />
					<div class="absolute inset-y-0 right-0 flex gap-4 pr-4">
						<button :disabled="inputDisabled" @click="sendMessage(userMessage)">
							<heroicons-paper-airplane-solid v-if="userMessage.length > 0" class="h-6 w-6" />
							<heroicons-paper-airplane v-else class="h-6 w-6" />
						</button>
						<button v-if="!rabbitHoleState.loading" :disabled="inputDisabled"
							:class="[ inputDisabled ? 'cursor-default text-neutral-focus' : 'text-primary' ]"
							@click="openFile({ multiple: false, accept: AcceptedContentTypes.join(', ') })">
							<heroicons-paper-clip-20-solid class="h-6 w-6" />
						</button>
						<div v-else class="flex grow items-center justify-center">
							<div role="status"
								class="inline-block h-6 w-6 animate-spin rounded-full border-2 border-solid border-current border-r-transparent align-[-0.125em] text-primary motion-reduce:animate-[spin_1.5s_linear_infinite]">
								<span
									class="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
							</div>
						</div>
					</div>
				</div>
				<button v-if="isSupported" class="btn-circle btn" :class="[isListening ? 'btn-ghost' : 'btn-primary']"
					:disabled="inputDisabled" @pointerdown="startRecording" @pointerup="stopRecording">
					<heroicons-microphone-solid class="h-6 w-6" />
				</button>
			</div>
		</div>
		<button class="btn-outline btn-primary btn-sm btn-circle btn fixed bottom-24 right-2 bg-base-100 md:right-4"
			@click="scrollToBottom">
			<heroicons-arrow-down-20-solid class="h-5 w-5" />
		</button>
	</div>
</template>
