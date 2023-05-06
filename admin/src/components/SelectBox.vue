<script setup lang="ts">
import { ref } from 'vue'
import { Listbox, ListboxButton, ListboxOptions, ListboxOption } from '@headlessui/vue'
import { Icon } from '@iconify/vue/dist/offline'
import chevronUpDownIcon from '@iconify-icons/heroicons/chevron-up-down-solid'

const props = defineProps<{
    list: {
        label: string,
        value: string
    }[],
    selected?: string
}>()

const selectedIndex = props.list.findIndex(v => v.value === props.selected)

const selectedElement = ref(selectedIndex != -1 ? props.list[selectedIndex] : props.list[0])

const emit = defineEmits(["update"])

defineExpose({
    selectedElement
})
</script>

<template>
    <Listbox v-model="selectedElement" @update:modelValue="value => emit('update', value)">
        <div class="relative">
            <ListboxButton
                class="relative w-full p-3 text-sm text-left rounded-lg shadow-lg cursor-default bg-base-100 focus:outline-none">
                <span class="block font-semibold truncate">{{ selectedElement.label }}</span>
                <span class="absolute inset-y-0 flex items-center pointer-events-none right-2">
                    <Icon :icon="chevronUpDownIcon" class="w-6 h-6" aria-hidden="true" />
                </span>
            </ListboxButton>
            <Transition leave-active-class="transition duration-100 ease-in" leave-from-class="opacity-100"
                leave-to-class="opacity-0">
                <ListboxOptions class="absolute w-full mt-2 overflow-auto text-sm rounded-md shadow-lg bg-base-100">
                    <ListboxOption v-for="element in list" :key="element.value" v-slot="{ active, selected }" as="template" :value="element">
                        <li :class="[
                                active ? 'bg-base-300' : '',
                                selected ? 'bg-primary text-base-100 font-semibold' : 'text-neutral',
                                'relative cursor-default select-none px-3 py-2',
                            ]">
                            <span class="block truncate">{{ element.label }}</span>
                        </li>
                    </ListboxOption>
                </ListboxOptions>
            </Transition>
        </div>
    </Listbox>
</template>
