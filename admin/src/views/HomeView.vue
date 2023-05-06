<script setup lang="ts">
import { Icon } from '@iconify/vue/dist/offline'
import microphoneIcon from '@iconify-icons/heroicons/microphone-solid'
import clipIcon from '@iconify-icons/heroicons/paper-clip-solid'
import airplaneIcon from '@iconify-icons/heroicons/paper-airplane'
import airplaneIconSolid from '@iconify-icons/heroicons/paper-airplane-solid'
import soundOnIcon from '@iconify-icons/akar-icons/sound-on'
import soundOffIcon from '@iconify-icons/akar-icons/sound-off'

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

const recordButton = ref<HTMLElement | null>(null), textArea = ref<HTMLElement | null>(null)
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
  return messagesState.value.loading || isListening.value || !messagesState.value.ready || Boolean(messagesState.value.error)
})

const randomDefaultMessages = selectRandomDefaultMessages()

/**
 * When the user starts recording and sound is enabled, an audio is played
 */
const longPressRecording = () => {
  if (isAudioEnabled.value) {
    playRec()
  }
  startRecording()
}

/**
 * When the user stops recording, the transcript will be sent to the messages service
 */
watchEffect(() => {
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

const generatePlaceholder = (isLoading: boolean, isRecording: boolean, error?: string) => {
  if (error) return 'Well, well, well, looks like something has gone amiss'
  if (isLoading) return 'The enigmatic Cheshire cat is pondering...'
  if (isRecording) return 'The curious Cheshire cat is all ear...'
  return 'Ask the Cheshire Cat...'
}
</script>

<template>
  <div class="flex flex-col self-center justify-center w-full max-w-screen-lg gap-4 grow">
    <div v-if="!messagesState.ready" class="self-center">
      <p v-if="messagesState.error" class="p-4 font-semibold bg-error w-fit rounded-xl">{{ messagesState.error }}</p>
      <p v-else>Getting ready...</p>
    </div>
    <div v-else class="flex flex-col w-full grow">
      <div v-if="messagesState.messages.length" class="flex flex-col grow">
        <div v-for="msg in messagesState.messages" :key="msg.id" 
          class="chat gap-y-1" :class="[ msg.sender === 'bot' ? 'chat-start' : 'chat-end' ]">
          <div class="px-2 font-semibold chat-header">
            {{ msg.sender === 'bot' ? '😺 Cheshire Cat' : 'You 👤' }}
          </div>
          <div class="chat-bubble">{{ msg.text }}</div>
        </div>
        <p v-if="messagesState.error" class="p-4 font-semibold bg-error w-fit rounded-xl">{{ messagesState.error }}</p>
        <p v-else-if="!messagesState.error && messagesState.loading">😺 Cheshire cat is thinking...</p>
      </div>
      <div v-else class="flex flex-col items-center justify-center gap-4 cursor-pointer grow">
        <div v-for="(msg, index) in randomDefaultMessages" :key="index"
          class="normal-case rounded-full shadow-xl btn" @click="sendMessage(msg)">
          {{ msg }}
        </div>
      </div>
    </div>
    <div class="flex items-end justify-center gap-4 mt-auto">
      <label class="bg-transparent border-none btn text-primary hover:bg-base-300 swap btn-circle">
        <input type="checkbox" class="modal-toggle" v-model="isAudioEnabled" />
        <Icon class="w-6 h-6 swap-off" :icon="soundOffIcon" />
        <Icon class="w-6 h-6 swap-on" :icon="soundOnIcon" />
      </label>
      <div class="relative w-full">
        <textarea ref="textArea" v-model="userMessage" :rows="isTwoLines ? '2' : '1'" :disabled="inputDisabled"
          class="block w-full pr-24 overflow-hidden !outline-none !ring-0 focus:border-2 resize-none textarea textarea-bordered focus:border-primary"
          :placeholder="generatePlaceholder(messagesState.loading, isListening, messagesState.error)">
        </textarea>
        <div class="absolute inset-y-0 right-0 flex gap-4 pr-4">
          <button :class="{ '!cursor-default': inputDisabled }" :disabled="inputDisabled" @click="sendMessage(userMessage)">
            <Icon class="w-6 h-6" :icon="userMessage.length ? airplaneIconSolid : airplaneIcon" />
          </button>
          <button v-if="!rabbitHoleState.loading" :disabled="inputDisabled" :class="{ 'cursor-default': inputDisabled }"
            @click="openFile({ multiple: false, accept: AcceptedContentTypes.join(', ') })">
            <Icon class="w-6 h-6 text-primary" :icon="clipIcon" />
          </button>
          <div v-else class="flex items-center justify-center grow">
            <div role="status"
              class="inline-block h-6 w-6 animate-spin rounded-full border-2 border-solid border-current border-r-transparent align-[-0.125em] text-primary motion-reduce:animate-[spin_1.5s_linear_infinite]">
              <span class="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
            </div>
          </div>
        </div>
      </div>
      <button ref="recordButton" v-if="isSupported" @mousedown="longPressRecording" @mouseup="stopRecording"
        class="btn btn-circle" :class="[ isListening ? 'btn-ghost' : 'btn-primary' ]">
        <Icon :icon="microphoneIcon" class="w-6 h-6" aria-hidden="true" />
      </button>
    </div>
  </div>
</template>
