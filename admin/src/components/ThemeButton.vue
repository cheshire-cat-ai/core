<script setup lang="ts">
import { useSettings } from '@stores/useSettings'

const store = useSettings()
const { toggleDark } = store
const { isDark } = storeToRefs(store)
</script>

<template>
	<button class="swap btn-ghost btn-square btn md:btn-sm" @click="toggleDark()">
		<input v-model="isDark" type="checkbox" class="modal-toggle">
		<heroicons-sun-solid class="swap-on h-6 w-6" />
		<heroicons-moon-solid class="swap-off h-6 w-6" />
	</button>
</template>
