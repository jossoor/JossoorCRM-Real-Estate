<template>
  <div
    v-if="title !== 'Data' && title !== 'Reservation'"
    class="mx-4 my-3 flex items-center justify-between text-lg font-medium sm:mx-10 sm:mb-4 sm:mt-8"
  >
    <div class="flex h-8 items-center text-xl font-semibold text-ink-gray-8">
      {{ __(title) }}
    </div>
    <Button
      v-if="title == 'Emails'"
      variant="solid"
      :label="__('New Email')"
      iconLeft="plus"
      @click="emailBox.show = true"
    />
    <Button
      v-else-if="title == 'Comments'"
      variant="solid"
      :label="__('New FeedBack')"
      iconLeft="plus"
      @click="emailBox.showComment = true"
    />
    <MultiActionButton
      v-else-if="title == 'Calls'"
      variant="solid"
      :options="callActions"
    />
    <Button
      v-else-if="title == 'Notes'"
      variant="solid"
      :label="__('New Note')"
      iconLeft="plus"
      @click="modalRef.showNote()"
    />
    <Button
      v-else-if="title == 'Tasks'"
      variant="solid"
      :label="__('New Task')"
      iconLeft="plus"
      @click="modalRef.showTask()"
    />
    <Button
      v-else-if="title == 'Attachments'"
      variant="solid"
      :label="__('Upload Attachment')"
      iconLeft="plus"
      @click="showFilesUploader = true"
    />
    <div class="flex gap-2 shrink-0" v-else-if="title == 'WhatsApp'">
      <Button
        :label="__('Send Template')"
        @click="showWhatsappTemplates = true"
      />
      <Button
        variant="solid"
        :label="__('New Message')"
        iconLeft="plus"
        @click="whatsappBox.show()"
      />
    </div>
  </div>
</template>
<script setup>
import MultiActionButton from '@/components/MultiActionButton.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import { globalStore } from '@/stores/global'
import { callEnabled } from '@/composables/settings'
import { computed, h } from 'vue'

const props = defineProps({
  tabs: Array,
  title: String,
  doc: Object,
  modalRef: Object,
  emailBox: Object,
  whatsappBox: Object,
})

const { makeCall } = globalStore()

defineModel()
const showWhatsappTemplates = defineModel('showWhatsappTemplates')
const showFilesUploader = defineModel('showFilesUploader')

const callActions = computed(() => {
  let actions = [
    {
      label: __('Log a Call'),
      icon: 'plus',
      onClick: () => props.modalRef.createCallLog(),
    },
    {
      label: __('Make a Call'),
      icon: h(PhoneIcon, { class: 'h-4 w-4' }),
      onClick: () => makeCall(props.doc.mobile_no),
      condition: () => callEnabled.value,
    },
  ]

  return actions.filter((action) =>
    action.condition ? action.condition() : true,
  )
})
</script>