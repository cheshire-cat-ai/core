<script setup lang="ts">
const props = defineProps<{
    list: {
        label: string,
        value: string
    }[],
    picked?: string
}>()

const selectedIndex = props.list.findIndex(v => v.value === props.picked)

const selectedElement = ref(selectedIndex != -1 ? props.list[selectedIndex] : props.list[0])

const emit = defineEmits<{
	(e: 'update', value: typeof props.list[number]): void
}>()

defineExpose({
    selectedElement
})
</script>

<template>
	<Listbox v-model="selectedElement" @update:modelValue="value => emit('update', value)">
		<div class="relative">
			<ListboxButton
				class="relative w-full cursor-default rounded bg-base-100 p-3 text-left text-sm shadow-md focus:outline-none">
				<span class="block truncate font-semibold">{{ selectedElement.label }}</span>
				<span class="pointer-events-none absolute inset-y-0 right-2 flex items-center">
					<heroicons-chevron-up-down-20-solid class="h-6 w-6" />
				</span>
			</ListboxButton>
			<Transition leave-active-class="transition duration-100 ease-in" leave-from-class="opacity-100"
				leave-to-class="opacity-0">
				<ListboxOptions class="absolute mt-2 w-full overflow-auto rounded bg-base-100 text-sm shadow-lg">
					<ListboxOption v-for="element in list" :key="element.value" v-slot="{ active, selected }" as="template" :value="element">
						<li :class="[
							active ? 'bg-base-300' : '',
							selected ? 'bg-primary font-semibold text-base-100' : 'text-neutral',
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
