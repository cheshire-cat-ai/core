<script setup lang="ts">
import { RouterView } from 'vue-router'
import Header from '@components/Header.vue'
import NotificationStack from '@components/NotificationStack.vue'
</script>

<template>
  <div class="flex flex-col min-h-screen transition-colors selection:bg-secondary-focus bg-base-100 scroll-smooth">
    <Header />
    <NotificationStack />
    <RouterView v-slot="{ Component }" class="p-4 grow">
      <template v-if="Component">
        <Transition mode="out-in"
          enter-active-class="animate__animated animate__fadeIn animate__fastest"
          leave-active-class="animate__animated animate__fadeOut animate__fastest">
          <KeepAlive>
            <component :is="Component"></component>
          </KeepAlive>
        </Transition>
      </template>
    </RouterView>
  </div>
</template>
