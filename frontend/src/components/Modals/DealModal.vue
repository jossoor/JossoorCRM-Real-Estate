<template>
  <Dialog v-model="show" :options="{ size: '3xl' }">
    <template #body>
      <div class="bg-surface-modal px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
              {{ __('Create Deal') }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button
              v-if="isManager() && !isMobileView"
              variant="ghost"
              class="w-7"
              :tooltip="__('Edit fields layout')"
              :icon="EditIcon"
              @click="openQuickEntryModal"
            />
            <Button
              variant="ghost"
              class="w-7"
              icon="x"
              @click="show = false"
            />
          </div>
        </div>
        <div>
          <div
            v-if="hasContactSections"
            class="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-3"
          >
            <div
              class="flex items-center gap-3 text-sm text-ink-gray-5"
            >
              <div>{{ __('Choose Existing Contact') }}</div>
              <Switch v-model="chooseExistingContact" />
            </div>
          </div>
          <div
            v-if="hasContactSections"
            class="h-px w-full border-t my-5"
          />
          <FieldLayout
            ref="fieldLayoutRef"
            v-if="tabs.data?.length"
            :tabs="tabs.data"
            :data="deal.doc"
            doctype="CRM Deal"
          />
          <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
        </div>
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Create')"
            :loading="isDealCreating"
            @click="createDeal"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import EditIcon from '@/components/Icons/EditIcon.vue'
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { isMobileView } from '@/composables/settings'
import { showQuickEntryModal, quickEntryProps } from '@/composables/modals'
import { useDocument } from '@/data/document'
import { capture } from '@/telemetry'
import { Switch, createResource } from 'frappe-ui'
import { computed, ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  defaults: Object,
})

const { getUser, isManager } = usersStore()
const { getDealStatus, statusOptions } = statusesStore()

const show = defineModel()
const router = useRouter()
const error = ref(null)

const { document: deal, triggerOnBeforeCreate } = useDocument('CRM Deal')

const hasContactSections = ref(true)

const isDealCreating = ref(false)
const chooseExistingContact = ref(false)
const fieldLayoutRef = ref(null)

watch(
  [chooseExistingContact],
  ([contact]) => {
    tabs.data.forEach((tab) => {
      tab.sections.forEach((section) => {
        if (section.name === 'contact_section') {
          section.hidden = !contact
        } else if (section.name === 'contact_details_section') {
          section.hidden = contact
        }
      })
    })
  },
)

const tabs = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['QuickEntry', 'CRM Deal'],
  params: { doctype: 'CRM Deal', type: 'Quick Entry' },
  auto: true,
  transform: (_tabs) => {
    hasContactSections.value = false

    _tabs.forEach((tab) => {
      tab.sections = (tab.sections || []).filter(
        (section) =>
          !['organization_section', 'organization_details_section'].includes(
            section.name,
          ),
      )

      tab.sections.forEach((section) => {
        section.columns?.forEach((column) => {
          if (
            ['contact_section', 'contact_details_section'].includes(section.name)
          ) {
            hasContactSections.value = true
          }

          column.fields = (column.fields || []).filter((field) => {
            const fieldname = typeof field === 'string' ? field : field.fieldname
            return fieldname !== 'organization'
          })

          column.fields.forEach((field) => {
            if (typeof field === 'object' && field.fieldname === 'status') {
              field.fieldtype = 'Select'
              field.options = dealStatuses.value
              field.prefix = getDealStatus(deal.doc.status)?.color
            }

            if (typeof field === 'object' && field.fieldtype === 'Table') {
              deal.doc[field.fieldname] = []
            }
          })
        })
      })
    })

    return _tabs
  },
})

const dealStatuses = computed(() => {
  let statuses = statusOptions('deal')
  if (!deal.doc.status) {
    deal.doc.status = statuses[0].value
  }
  return statuses
})

async function createDeal() {
  if (deal.doc.website && !deal.doc.website.startsWith('http')) {
    deal.doc.website = 'https://' + deal.doc.website
  }

  deal.doc['organization'] = null

  if (chooseExistingContact.value) {
    deal.doc['first_name'] = null
    deal.doc['last_name'] = null
    deal.doc['email'] = null
    deal.doc['mobile_no'] = null
  } else {
    deal.doc['contact'] = null
  }

  await triggerOnBeforeCreate?.()

  createResource({
    url: 'crm.fcrm.doctype.crm_deal.crm_deal.create_deal',
    params: { args: deal.doc },
    auto: true,
    validate() {
      error.value = null
      if (chooseExistingContact.value) {
        if (!deal.doc.contact) {
          error.value = __('Contact is required')
          return error.value
        }
      } else {
        if (!deal.doc.first_name || !deal.doc.first_name.trim()) {
          error.value = __('First Name is required')
          return error.value
        }
        
        const invalidChars = [';','<','>','{','}','[',']']
        if (invalidChars.some(ch => String(deal.doc.first_name || '').includes(ch))) {
          error.value = __('First Name contains invalid characters')
          return error.value
        }

        if (String(deal.doc.first_name || '').length > 50) {
          error.value = __('First Name cannot exceed 50 characters')
          return error.value
        }

        if (deal.doc.last_name && String(deal.doc.last_name || '').length > 140) {
          error.value = __('Last Name cannot exceed 140 characters')
          return error.value
        }

        if (!deal.doc.mobile_no || !deal.doc.mobile_no.trim()) {
          error.value = __('Mobile No is mandatory')
          return error.value
        }

        if (!isValidPhone(deal.doc.mobile_no)) {
          error.value = __('Enter a valid Egyptian (01xxxxxxxxx) or Saudi (05xxxxxxxx) mobile number')
          return error.value
        }
        
        if (deal.doc.email) {
          if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(deal.doc.email).trim())) {
            error.value = __('Invalid Email address')
            return error.value
          }
          if (String(deal.doc.email).length > 140) {
            error.value = __('Email cannot exceed 140 characters')
            return error.value
          }
        }
      }

      if (deal.doc.organization_name && String(deal.doc.organization_name).length > 140) {
        error.value = __('Organization Name cannot exceed 140 characters')
        return error.value
      }

      if (deal.doc.annual_revenue) {
        if (typeof deal.doc.annual_revenue === 'string') {
          deal.doc.annual_revenue = deal.doc.annual_revenue.replace(/,/g, '')
        }
        const rev = Number(deal.doc.annual_revenue)
        if (isNaN(rev) || rev < 0) {
          error.value = __('Annual Revenue should be a positive number')
          return error.value
        }
        deal.doc.annual_revenue = rev
      }
      
      if (!deal.doc.status) {
        error.value = __('Status is required')
        return error.value
      }
      
      isDealCreating.value = true
    },
    onSuccess(name) {
      capture('deal_created')
      isDealCreating.value = false
      show.value = false
      router.push({ name: 'Deal', params: { dealId: name } })
    },
    onError(err) {
      isDealCreating.value = false
      if (!err.messages) {
        error.value = err.message
        return
      }
      error.value = err.messages.join('\n')
    },
  })
}

function cleanRaw(number) {
  if (!number) return ''
  const arabic = { '٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9' }
  let n = String(number).replace(/[٠-٩]/g, d => arabic[d])
  let out = ''
  for (let i = 0; i < n.length; i++) {
    if (/\d/.test(n[i]) || (n[i] === '+' && i === 0)) out += n[i]
  }
  return out
}

function normalizePhone(number) {
  const n = cleanRaw(number)
  if (!n) return ''

  // Explicit country code
  if (n.startsWith('+20'))    return '+20'  + n.slice(3)
  if (n.startsWith('0020'))   return '+20'  + n.slice(4)
  if (n.startsWith('+966'))   return '+966' + n.slice(4)
  if (n.startsWith('00966'))  return '+966' + n.slice(5)

  // Country code without +/00
  if (n.startsWith('20')  && n.length === 12) return '+20'  + n.slice(2)
  if (n.startsWith('966') && n.length === 12) return '+966' + n.slice(3)

  // Local shape — uniquely identifies country
  if (n.length === 11 && n.startsWith('01') && '0125'.includes(n[2])) return '+20'  + n.slice(1)  // Egypt mobile
  if (n.length === 10 && n.startsWith('05'))                           return '+966' + n.slice(1)  // Saudi mobile
  if (n.length === 10 && n[0] === '1'       && '0125'.includes(n[1])) return '+20'  + n           // Egypt mobile no-0
  if (n.length === 10 && n[0] === '0'       && '23'.includes(n[1]))   return '+20'  + n.slice(1)  // Egypt landline
  if (n.length === 10 && n.startsWith('01') && '1234567'.includes(n[2])) return '+966' + n.slice(1) // Saudi landline
  if (n.length === 9  && n.startsWith('5'))                            return '+966' + n           // Saudi mobile no-0

  return n // unknown — return cleaned
}

function isValidPhone(number) {
  const e164 = normalizePhone(number)
  return e164.startsWith('+20') || e164.startsWith('+966')
}

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  quickEntryProps.value = { doctype: 'CRM Deal' }
  nextTick(() => (show.value = false))
}

onMounted(() => {
  deal.doc = { no_of_employees: '1-10' }
  Object.assign(deal.doc, props.defaults)

  if (!deal.doc.deal_owner) {
    deal.doc.deal_owner = getUser().name
  }
  if (!deal.doc.status && dealStatuses.value[0].value) {
    deal.doc.status = dealStatuses.value[0].value
  }
})
</script>
