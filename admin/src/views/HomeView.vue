<script setup lang="ts">
import { useRabbitHole } from '@stores/useRabbitHole'
import { useMessages } from '@stores/useMessages'
import { useSound } from '@vueuse/sound'
import { AcceptedContentTypes } from '@services/RabbitHole'
import { useSettings } from '@stores/useSettings'
import ModalBox from '@components/ModalBox.vue'

const messagesStore = useMessages()
const { dispatchMessage, selectRandomDefaultMessages } = messagesStore
const { currentState: messagesState } = storeToRefs(messagesStore)

const textArea = ref<HTMLElement>()
const userMessage = ref(''), insertedURL = ref(''), isTwoLines = ref(false)
const modalBox = ref<InstanceType<typeof ModalBox>>()

const { isListening, isSupported, toggle: toggleRecording, result: transcript } = useSpeechRecognition()
const { open: openFile, onChange: onFileChange } = useFileDialog()
const { play: playPop } = useSound('pop.mp3')
const { play: playRec } = useSound('start-rec.mp3')

const filesStore = useRabbitHole()
const { sendFile, sendWebsite } = filesStore
const { currentState: rabbitHoleState } = storeToRefs(filesStore)

const { isAudioEnabled } = storeToRefs(useSettings())

const inputDisabled = computed(() => {
	return messagesState.value.loading || !messagesState.value.ready || Boolean(messagesState.value.error)
})

const randomDefaultMessages = selectRandomDefaultMessages()

/**
 * Handles the file upload change by calling the onUpload callback if it exists.
 */
onFileChange(files => {
	if (files == null) return
	sendFile(files[0])
})

/**
 * When the user stops recording, the transcript will be sent to the messages service
 */
watchEffect(() => {
	if (transcript.value === '') return
	userMessage.value = transcript.value
})

/**
 * Toggle recording and plays an audio if enabled
 */
const toggleListening = () => {
	toggleRecording()
	if (isListening.value && isAudioEnabled.value) playRec()
}

/**
 * Checks if the textarea needs to be multiline and updates the state accordingly.
 */
watchEffect(() => {
	if (!textArea.value || !userMessage.value) {
		isTwoLines.value = false
		return
	}
	const letterWidth = 8.275
	const isMultiLine = letterWidth * userMessage.value.length > textArea.value.offsetWidth
	const hasLineBreak = !!(/\r|\n/.exec(userMessage.value))
	isTwoLines.value = (textArea.value && !userMessage.value) || (isMultiLine || hasLineBreak)
})

/**
 * When a new message arrives, the chat will be scrolled to bottom.
 * If audio is enabled, a pop sound will be played.
 */
watchDeep(messagesState, () => {
	scrollToBottom()
	if (messagesState.value.messages.length > 0 && isAudioEnabled.value) playPop()
}, { flush: 'post' })

/**
 * Dispatches the inserted url to the RabbitHole service and closes the modal.
 */
const dispatchWebsite = () => {
	if (!insertedURL.value) return
	sendWebsite(insertedURL.value)
	modalBox.value?.toggleModal()
}

/**
 * Dispatches the user's message to the Messages service.
 */
const sendMessage = (message: string) => {
	if (message === '') return
	userMessage.value = ''
	dispatchMessage(message)
}

/**
 * Prevent sending the message if the shift key is pressed.
 */
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
	<div class="flex w-full max-w-screen-lg flex-col justify-center gap-4 self-center overflow-hidden !pt-0 pb-16 text-sm md:!pb-20">
		<div v-if="!messagesState.ready" class="flex grow items-center justify-center self-center">
			<p v-if="messagesState.error" class="w-fit rounded bg-error p-4 font-semibold text-base-100">
				{{ messagesState.error }}
			</p>
			<p v-else class="text-lg font-medium text-neutral">
				Getting ready...
			</p>
		</div>
		<div v-else-if="messagesState.messages.length" class="flex grow flex-col overflow-y-auto pt-10">
			<MessageBox v-for="msg in messagesState.messages"
				:key="msg.id"
				:sender="msg.sender"
				:text="msg.text"
				:why="msg.sender === 'bot' ? JSON.stringify(msg.why) : ''" />
			<p v-if="messagesState.error" class="w-fit rounded bg-error p-4 font-semibold text-base-100">
				{{ messagesState.error }}
			</p>
			<p v-else-if="!messagesState.error && messagesState.loading" class="ml-2">
				<span class="text-lg">😺</span>
				<span class="ml-10">Cheshire cat is thinking...</span>
			</p>
		</div>
		<div v-else class="flex grow cursor-pointer flex-col items-center justify-center gap-4">
			<div v-for="(msg, index) in randomDefaultMessages" :key="index" class="btn rounded-lg font-normal normal-case shadow-xl"
				@click="sendMessage(msg)">
				{{ msg }}
			</div>
		</div>
		<div class="fixed bottom-0 left-0 flex w-full items-center justify-center bg-gradient-to-t from-base-100 px-2 py-4">
			<div class="flex w-full max-w-screen-lg items-center gap-2 md:gap-4">
				<label class="swap btn-circle btn border-none bg-transparent text-primary hover:bg-base-300">
					<input v-model="isAudioEnabled" type="checkbox" class="modal-toggle">
					<akar-icons-sound-on class="swap-on h-6 w-6" />
					<akar-icons-sound-off class="swap-off h-6 w-6" />
				</label>
				<div class="relative w-full">
					<textarea ref="textArea" v-model="userMessage" :rows="isTwoLines ? '2' : '1'" :disabled="inputDisabled"
						class="textarea-bordered textarea block w-full resize-none overflow-hidden border-2 !pr-20 !outline-none !ring-0 transition focus:border-2 focus:border-primary"
						:placeholder="generatePlaceholder(messagesState.loading, isListening, messagesState.error)" @keydown="preventSend" />
					<div class="absolute inset-y-0 right-0 flex gap-1 pr-2">
						<button :disabled="inputDisabled"
							class="btn-outline btn-sm btn-circle btn self-center border-none text-neutral hover:!bg-transparent hover:text-neutral disabled:bg-transparent"
							@click="sendMessage(userMessage)">
							<heroicons-paper-airplane-solid v-if="userMessage.length > 0" class="h-6 w-6" />
							<heroicons-paper-airplane v-else class="h-6 w-6" />
						</button>
						<Menu as="div" class="dropdown-top dropdown-end dropdown self-center">
							<MenuButton :disabled="inputDisabled || rabbitHoleState.loading"
								class="btn-outline btn-primary btn-sm btn-circle btn border-none hover:!bg-transparent hover:!text-primary-focus disabled:bg-transparent">
								<heroicons-paper-clip-20-solid class="h-6 w-6" />
							</MenuButton>
							<MenuItems class="dropdown-content !-right-1/4 mb-4 flex flex-col gap-2 rounded bg-base-200 p-2 shadow-lg focus:outline-none">
								<MenuItem as="button" class="btn-info btn-square btn-sm btn" @click="modalBox?.toggleModal()">
									<heroicons-globe-alt class="h-6 w-6" />
								</MenuItem>
								<MenuItem as="button" class="btn-warning btn-square btn-sm btn"
									@click="openFile({ multiple: false, accept: AcceptedContentTypes.join(', ') })">
									<heroicons-document-text-solid class="h-6 w-6" />
								</MenuItem>
							</MenuItems>
						</Menu>
					</div>
				</div>
				<button v-if="isSupported" class="btn-primary btn-circle btn" :class="[isListening ? 'btn-outline glass' : '']"
					:disabled="inputDisabled" @click="toggleListening">
					<heroicons-microphone-solid class="h-6 w-6" />
				</button>
			</div>
		</div>
		<button class="btn-outline btn-primary btn-sm btn-circle btn fixed bottom-20 right-2 bg-base-100 md:right-4"
			@click="scrollToBottom">
			<heroicons-arrow-down-20-solid class="h-5 w-5" />
		</button>
		<ModalBox ref="modalBox">
			<div class="flex flex-col items-center justify-center gap-2 text-neutral">
				<h3 class="text-lg font-bold">
					Insert URL
				</h3>
				<p>Write down the URL yo want the Cat to digest :</p>
				<input v-model="insertedURL" type="text" placeholder="Enter url..."
					class="input-bordered input-primary input input-sm my-4 w-full">
				<button class="btn-primary btn-sm btn" @click="dispatchWebsite">
					Send
				</button>
			</div>
		</ModalBox>
	</div>
</template>
