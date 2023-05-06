<script setup lang="ts">
import { ref } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { Icon } from '@iconify/vue/dist/offline'
import markIcon from '@iconify-icons/heroicons/x-mark-solid'

defineProps<{
    title: string
}>()

const open = ref(false)

const togglePanel = () => open.value = !open.value

defineExpose({
    togglePanel, open
})
</script>

<template>
    <TransitionRoot as="template" :show="open">
        <Dialog as="div" class="relative z-10" @close="open = false">
            <TransitionChild as="template" enter="ease-in-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
                leave="ease-in-out duration-300" leave-from="opacity-100" leave-to="opacity-0">
                <div class="fixed inset-0 transition-opacity bg-opacity-50 bg-base-100" />
            </TransitionChild>
            <div class="fixed inset-0 overflow-hidden">
                <div class="absolute inset-0 overflow-hidden">
                    <div class="fixed inset-y-0 right-0 flex max-w-full pointer-events-none">
                        <TransitionChild as="template" enter="transform transition ease-in-out duration-500"
                            enter-from="translate-x-full" enter-to="translate-x-0"
                            leave="transform transition ease-in-out duration-500" leave-from="translate-x-0"
                            leave-to="translate-x-full">
                            <DialogPanel class="relative w-screen pointer-events-auto md:max-w-xl">
                                <div class="flex flex-col h-full overflow-y-auto shadow-xl bg-base-300">
                                    <div class="flex items-center justify-between gap-2 p-2.5 shadow-xl">
                                        <DialogTitle class="text-lg font-semibold">{{ title }}</DialogTitle>
                                        <button class="btn btn-sm btn-error btn-square"
                                            @click="open = false">
                                            <span class="sr-only">Close panel</span>
                                            <Icon :icon="markIcon" class="w-6 h-6" aria-hidden="true" />
                                        </button>
                                    </div>
                                    <div class="relative flex flex-col flex-1 p-4">
                                        <slot />
                                    </div>
                                </div>
                            </DialogPanel>
                        </TransitionChild>
                    </div>
                </div>
            </div>
        </Dialog>
    </TransitionRoot>
</template>
