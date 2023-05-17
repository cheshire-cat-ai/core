export const useSettings = defineStore('settings', () => {
  const isAudioEnabled = useLocalStorage('isAudioEnabled', true)
  const isDark = useDark({
    storageKey: 'currentTheme',
    selector: 'html',
    disableTransition: false,
    attribute: 'data-theme',
    valueDark: 'dark',
    valueLight: 'light'
  })

  const toggleDark = useToggle(isDark)

  return {
    isAudioEnabled, isDark, toggleDark
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useSettings, import.meta.hot))
}
