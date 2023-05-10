export const useSettings = defineStore('settings', () => {
  const isAudioEnabled = ref(true)
  const currentTheme = ref("white")
  
  const toggleAudio = () => isAudioEnabled.value = !isAudioEnabled.value

  const switchTheme = () => currentTheme.value = currentTheme.value === 'white' ? 'dark' : 'white'

  return {
    isAudioEnabled, toggleAudio, currentTheme, switchTheme
  }
})
