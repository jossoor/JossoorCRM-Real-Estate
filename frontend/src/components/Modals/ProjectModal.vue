<template>
  <div
    v-if="modelValue"
    class="fixed inset-0 z-[1000] flex items-center justify-center"
    @keydown.esc="close"
  >
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/40" @click="close"></div>

    <!-- Panel -->
    <div class="relative z-10 w-[95vw] max-w-5xl max-h-[90vh] bg-white dark:bg-gray-900 rounded-2xl shadow-xl overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between px-5 py-4 border-b dark:border-gray-800">
        <h2 class="text-lg font-semibold">
          {{ isEditIntent ? __('Edit Project') : __('Create Project') }}
        </h2>
        <Button variant="subtle" @click="close">{{ __('Close') }}</Button>
      </div>

      <!-- Body -->
      <div class="p-5 overflow-y-auto" style="max-height: calc(90vh - 120px)">
        <div v-if="loading" class="text-sm text-ink-gray-5">{{ __('Loading…') }}</div>

        <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Left: fields -->
          <div class="space-y-4 lg:col-span-2">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

              <!-- Project Name -->
              <div ref="ref_project_name" class="md:col-span-2">
                <label class="block text-sm mb-1">
                  {{ __('Project Name') }} <span class="text-red-500">*</span>
                </label>
                <Input
                  v-model="form.project_name"
                  :maxlength="PROJECT_NAME_MAX"
                  @blur="validateProjectName"
                />
                <div class="flex justify-between mt-0.5">
                  <span v-if="projectNameError" class="text-xs text-red-500">{{ projectNameError }}</span>
                  <span class="text-xs text-gray-400 ml-auto">
                    {{ (form.project_name || '').length }} / {{ PROJECT_NAME_MAX }}
                  </span>
                </div>
              </div>

              <!-- Status -->
              <div>
                <label class="block text-sm mb-1">{{ __('Status') }} <span class="text-red-500">*</span></label>
                <Select :options="selectOptions('status')" v-model="form.status" placeholder="Select" />
              </div>

              <!-- Exclusivity -->
              <div>
                <label class="block text-sm mb-1">{{ __('Exclusivity') }}</label>
                <Select :options="selectOptions('exclusivity')" v-model="form.exclusivity" placeholder="Select" />
              </div>

              <!-- Naming Series -->
              <div v-if="hasNamingSeries" ref="ref_naming_series">
                <label class="block text-sm mb-1">
                  {{ __('Naming Series') }} <span v-if="namingSeriesReqd" class="text-red-500">*</span>
                </label>
                <Select
                  :options="namingSeriesOptions.map(s => ({ label: s, value: s }))"
                  v-model="form.naming_series"
                  placeholder="Select series"
                />
              </div>

              <!-- Developer -->
              <div>
                <label class="block text-sm mb-1">{{ __('Developer') }}</label>
                <Input v-model="form.developer" />
              </div>

              <!-- City / District -->
              <div>
                <label class="block text-sm mb-1">{{ __('City') }}</label>
                <Input v-model="form.city" />
              </div>
              <div>
                <label class="block text-sm mb-1">{{ __('District') }}</label>
                <Input v-model="form.district" />
              </div>

              <!-- Location (URL) - plain text input, not a dropdown -->
              <div class="md:col-span-2" ref="ref_location">
                <label class="block text-sm mb-1">{{ __('Location (Google Maps URL)') }}</label>
                <Input
                  v-model="form.location"
                  placeholder="https://maps.google.com/..."
                  @blur="validateLocation"
                />
                <span v-if="locationError" class="text-xs text-red-500">{{ locationError }}</span>
              </div>

              <!-- Marketing Campaign -->
              <div class="md:col-span-2">
                <label class="block text-sm mb-1">{{ __('Marketing Campaign') }}</label>
                <Input v-model="form.marketing_campaign" />
              </div>

              <!-- Prices with cross-validation -->
              <div>
                <label class="block text-sm mb-1">{{ __('Min Price') }}</label>
                <Input v-model="form.min_price" type="number" @blur="validatePrices" />
              </div>
              <div>
                <label class="block text-sm mb-1">{{ __('Max Price') }}</label>
                <Input v-model="form.max_price" type="number" @blur="validatePrices" />
              </div>
              <div v-if="priceError" class="md:col-span-2">
                <span class="text-xs text-red-500">{{ priceError }}</span>
              </div>

              <!-- Areas -->
              <div>
                <label class="block text-sm mb-1">{{ __('Land Area (m²)') }}</label>
                <Input v-model="form.land_area" type="number" />
              </div>
              <div>
                <label class="block text-sm mb-1">{{ __('Project Buildup Area (m²)') }}</label>
                <Input v-model="form.project_buildup_area" type="number" />
              </div>

              <!-- Generic "Area" -->
              <div class="md:col-span-2">
                <label class="block text-sm mb-1">{{ __('Area') }}</label>
                <Input v-model="form.area" placeholder="e.g., 80–250 sqm units" />
              </div>

              <!-- Floors / Furnishing -->
              <div>
                <label class="block text-sm mb-1">{{ __('Floors') }}</label>
                <Input v-model="form.floors" type="number" />
              </div>
              <div>
                <label class="block text-sm mb-1">{{ __('Furnishing') }}</label>
                <Select :options="selectOptions('furnishing')" v-model="form.furnishing" placeholder="Select" />
              </div>

              <!-- Down Payment -->
              <div>
                <label class="block text-sm mb-1">{{ __('Down Payment (%)') }}</label>
                <Input v-model="form.down_payment" type="number" />
              </div>

              <!-- Categories -->
              <div class="md:col-span-2">
                <label class="block text-sm mb-1">
                  {{ __('Categories') }} <span class="text-red-500">*</span>
                </label>
                <Select
                  :options="selectOptions('categories')"
                  v-model="form.categories"
                  placeholder="Select a category"
                />
              </div>

              <!-- Payment Plan with char counter -->
              <div class="md:col-span-2">
                <label class="block text-sm mb-1">{{ __('Payment Plan') }}</label>
                <Textarea v-model="form.payment_plan" rows="3" :maxlength="PAYMENT_PLAN_MAX" />
                <div class="flex justify-between mt-0.5">
                  <span v-if="paymentPlanError" class="text-xs text-red-500">{{ paymentPlanError }}</span>
                  <span class="text-xs text-gray-400 ml-auto">
                    {{ (form.payment_plan || '').length }} / {{ PAYMENT_PLAN_MAX }}
                  </span>
                </div>
              </div>

              <!-- Description with char counter -->
              <div class="md:col-span-2">
                <label class="block text-sm mb-1">{{ __('Description') }}</label>
                <Textarea v-model="form.description" rows="4" :maxlength="DESCRIPTION_MAX" />
                <div class="flex justify-between mt-0.5">
                  <span v-if="descriptionError" class="text-xs text-red-500">{{ descriptionError }}</span>
                  <span class="text-xs text-gray-400 ml-auto">
                    {{ (form.description || '').length }} / {{ DESCRIPTION_MAX }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Right: cover + logo + brochure + gallery -->
          <div class="space-y-6">
            <!-- Cover -->
            <div>
              <label class="block text-sm mb-1">{{ __('Cover Image') }}</label>
              <div class="rounded-lg border bg-gray-50 dark:bg-gray-900 overflow-hidden h-40 flex items-center justify-center">
                <img v-if="coverPreviewSrc" :src="coverPreviewSrc" alt="cover" class="w-full h-full object-cover" />
                <div v-else class="text-sm opacity-60">{{ __('No image selected') }}</div>
              </div>
              <div class="mt-2 flex items-center gap-2">
                <input ref="coverInput" type="file" accept="image/*" class="hidden" @change="onCoverPicked" />
                <Button size="sm" @click="coverInput?.click()">
                  <template #prefix><FeatherIcon name="upload-cloud" class="h-4" /></template>
                  {{ __('Choose') }}
                </Button>
                <Button v-if="coverFile || form.cover_image" size="sm" variant="subtle" @click="clearCover()">
                  <template #prefix><FeatherIcon name="x" class="h-4" /></template>
                  {{ __('Remove') }}
                </Button>
                <span v-if="form.cover_image && !coverFile" class="text-xs opacity-70 truncate">
                  {{ __('Current:') }} {{ basename(form.cover_image) }}
                </span>
              </div>
            </div>

            <!-- Logo - with live preview -->
            <div>
              <label class="block text-sm mb-1">{{ __('Logo') }}</label>
              <div class="rounded-lg border bg-gray-50 dark:bg-gray-900 overflow-hidden h-24 flex items-center justify-center">
                <img v-if="logoPreviewSrc" :src="logoPreviewSrc" alt="logo" class="max-h-full max-w-full object-contain p-2" />
                <div v-else class="text-xs opacity-60 px-2 text-center">{{ __('No logo selected') }}</div>
              </div>
              <div class="mt-2 flex items-center gap-2">
                <input ref="logoInput" type="file" accept="image/*" class="hidden" @change="onLogoPicked" />
                <Button size="sm" @click="logoInput?.click()">
                  <template #prefix><FeatherIcon name="upload-cloud" class="h-4" /></template>
                  {{ __('Choose') }}
                </Button>
                <Button v-if="logoFile || form.logo" size="sm" variant="subtle" @click="clearLogo()">
                  <template #prefix><FeatherIcon name="x" class="h-4" /></template>
                  {{ __('Remove') }}
                </Button>
              </div>
            </div>

            <!-- Brochure - with download link when existing -->
            <div>
              <label class="block text-sm mb-1">{{ __('Brochure (PDF)') }}</label>
              <div class="rounded-lg border bg-gray-50 dark:bg-gray-900 p-2 min-h-[40px] flex items-center">
                <a
                  v-if="form.brochure && !brochureFile"
                  :href="form.brochure"
                  target="_blank"
                  rel="noopener"
                  class="text-xs text-blue-600 underline break-all"
                >
                  {{ basename(form.brochure) }}
                </a>
                <span v-else-if="brochureFile" class="text-xs break-all opacity-80">{{ brochureFile.name }}</span>
                <span v-else class="text-xs opacity-60">{{ __('No file selected') }}</span>
              </div>
              <div class="mt-2 flex items-center gap-2">
                <input ref="brochureInput" type="file" accept="application/pdf" class="hidden" @change="onBrochurePicked" />
                <Button size="sm" @click="brochureInput?.click()">
                  <template #prefix><FeatherIcon name="upload-cloud" class="h-4" /></template>
                  {{ __('Choose') }}
                </Button>
                <Button v-if="brochureFile || form.brochure" size="sm" variant="subtle" @click="clearBrochure()">
                  <template #prefix><FeatherIcon name="x" class="h-4" /></template>
                  {{ __('Remove') }}
                </Button>
              </div>
            </div>

            <!-- Gallery -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="block text-sm">{{ __('Gallery') }}</label>
                <div class="flex items-center gap-2">
                  <input ref="galleryInput" type="file" accept="image/*" class="hidden" multiple @change="onGalleryPicked" />
                  <Button size="sm" :disabled="!form.name" @click="galleryInput?.click()">
                    <template #prefix><FeatherIcon name="images" class="h-4" /></template>
                    {{ form.name ? __('Add Images') : __('Save first to add images') }}
                  </Button>
                </div>
              </div>

              <div class="grid grid-cols-3 gap-2">
                <div
                  v-for="(img, i) in galleryRows"
                  :key="'g-existing-' + i"
                  class="rounded-lg overflow-hidden border bg-gray-50 dark:bg-gray-900 relative"
                >
                  <img :src="img.image" class="w-full h-24 object-cover" />
                </div>

                <div
                  v-for="(blob, i) in queuedGallery"
                  :key="'g-queued-' + i"
                  class="rounded-lg overflow-hidden border bg-gray-50 dark:bg-gray-900 relative"
                >
                  <img :src="URL.createObjectURL(blob)" class="w-full h-24 object-cover" />
                  <div class="absolute inset-0 bg-black/10 pointer-events-none"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <p v-if="errorMsg" class="text-red-600 mt-3 text-sm whitespace-pre-line">{{ errorMsg }}</p>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between px-5 py-4 border-t dark:border-gray-800">
        <div />
        <div class="flex items-center gap-3">
          <Button variant="subtle" @click="close">{{ __('Cancel') }}</Button>
          <Button :loading="saving" variant="solid" @click="save">
            {{ isEditIntent ? __('Save') : __('Create') }}
          </Button>
        </div>
      </div>
    </div>
  </div>

  <!-- Custom delete-confirmation dialog -->
  <div v-if="confirmDialog.show" class="fixed inset-0 z-[1100] flex items-center justify-center">
    <div class="absolute inset-0 bg-black/40" @click="confirmDialog.show = false"></div>
    <div class="relative z-10 w-[90vw] max-w-sm bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-6">
      <h3 class="text-base font-semibold mb-2">{{ confirmDialog.title }}</h3>
      <p class="text-sm text-gray-600 dark:text-gray-300 mb-6">{{ confirmDialog.message }}</p>
      <div class="flex justify-end gap-3">
        <Button variant="subtle" @click="confirmDialog.show = false">{{ __('Cancel') }}</Button>
        <Button variant="solid" class="bg-red-600 hover:bg-red-700 text-white" @click="confirmDialog.onConfirm?.()">
          {{ __('Delete') }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Input, Textarea, Select, FeatherIcon, call } from 'frappe-ui'
import { ref, watch, computed, reactive } from 'vue'

// Character limits (must match backend constants)
const PROJECT_NAME_MAX = 140
const DESCRIPTION_MAX  = 2000
const PAYMENT_PLAN_MAX = 1000

// Canonical furnishing values matching the DocType JSON options exactly.
// The backend will also normalise, but we fix it client-side first so the
// UI select shows the right selected value.
const FURNISHING_CANONICAL = {
  'unfurnished':     'Unfurnished',
  'semi-furnished':  'Semi-Furnished',
  'semi furnished':  'Semi-Furnished',
  'semifurnished':   'Semi-Furnished',
  'fully-furnished': 'Fully-Furnished',
  'fully furnished': 'Fully-Furnished',
  'fullyfurnished':  'Fully-Furnished',
}

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  project: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'saved'])

/* ---------- modal open state ---------- */
const modelValue = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})
const isEditIntent = ref(false)

/* ---------- focus refs ---------- */
const ref_project_name = ref(null)
const ref_naming_series = ref(null)
const ref_location = ref(null)

/* ---------- inline validation state ---------- */
const projectNameError = ref('')
const locationError    = ref('')
const priceError       = ref('')
const descriptionError = ref('')
const paymentPlanError = ref('')

/* ---------- custom confirm dialog ---------- */
const confirmDialog = reactive({
  show: false,
  title: '',
  message: '',
  onConfirm: null,
})
function showConfirm(title, message, onConfirm) {
  confirmDialog.title = title
  confirmDialog.message = message
  confirmDialog.onConfirm = () => { confirmDialog.show = false; onConfirm() }
  confirmDialog.show = true
}

/* ---------- meta + dynamic select options ---------- */
const metaFields = ref([])
const selectOptionsMap = ref({})

/* Canonical options — values must match the DocType JSON exactly */
const FALLBACK_STATUS = [
  'Available', 'On Lease', 'On Sale', 'Reserved',
  'Off lease in 3 months', 'Leased', 'Sold', 'Removed',
].map(v => ({ label: v, value: v }))

const FALLBACK_EXCLUSIVITY = [
  'Exclusive', 'Non-Exclusive',
].map(v => ({ label: v, value: v }))

const FALLBACK_CATEGORIES = [
  'Residential', 'Commercial', 'Administrative',
].map(v => ({ label: v, value: v }))

// Values match JSON: "Unfurnished\nSemi-Furnished\nFully-Furnished"
const FALLBACK_FURNISHING = [
  { label: 'Unfurnished',    value: 'Unfurnished' },
  { label: 'Semi-Furnished', value: 'Semi-Furnished' },
  { label: 'Fully-Furnished',value: 'Fully-Furnished' },
]

function selectOptions(fieldname) {
  return selectOptionsMap.value[fieldname] || []
}

/* naming series */
const hasNamingSeries = ref(false)
const namingSeriesReqd = ref(false)
const namingSeriesOptions = ref([])

/* ---------- form model ---------- */
const blank = () => ({
  doctype: 'Real Estate Project',
  name: null,
  project_name: '',
  status: '',
  exclusivity: '',
  developer: '',
  city: '',
  district: '',
  location: '',
  marketing_campaign: '',
  min_price: null,
  max_price: null,
  land_area: null,
  project_buildup_area: null,
  area: '',
  down_payment: null,
  floors: null,
  furnishing: '',
  categories: '',
  payment_plan: '',
  description: '',
  cover_image: '',
  logo: '',
  brochure: '',
  naming_series: undefined,
  company: undefined,
})
const form = ref(blank())

/* ---------- ui state ---------- */
const loading = ref(false)
const saving  = ref(false)
const errorMsg = ref('')

/* ---------- files ---------- */
const coverInput = ref(null)
const coverFile = ref(null)
const logoInput = ref(null)
const logoFile = ref(null)
const brochureInput = ref(null)
const brochureFile = ref(null)
const previewKey = ref(Date.now())

const coverPreviewSrc = computed(() => {
  if (coverFile.value) return URL.createObjectURL(coverFile.value)
  if (!form.value.cover_image) return ''
  const q = form.value.cover_image.includes('?') ? '&' : '?'
  return `${form.value.cover_image}${q}v=${previewKey.value}`
})

// Logo preview — show actual image, not just filename
const logoPreviewSrc = computed(() => {
  if (logoFile.value) return URL.createObjectURL(logoFile.value)
  if (!form.value.logo) return ''
  const q = form.value.logo.includes('?') ? '&' : '?'
  return `${form.value.logo}${q}v=${previewKey.value}`
})

/* ---------- gallery ---------- */
const galleryInput = ref(null)
const galleryRows = ref([])
const queuedGallery = ref([])

/* ---------- open / load ---------- */
watch(
  [() => props.modelValue, () => props.project],
  async ([open]) => {
    if (!open) return
    resetUploadsAndGallery()
    clearInlineErrors()
    errorMsg.value = ''
    await loadMetaAndDefaults()

    isEditIntent.value = !!props.project?.name
    if (isEditIntent.value) {
      await fetchAndBind(props.project.name)
    } else {
      form.value = applyMetaDefaults(blank())
      setDefaultSelectsFromOptions()
    }
  },
  { immediate: true }
)

/* ---------- helpers ---------- */
function close() {
  errorMsg.value = ''
  clearInlineErrors()
  modelValue.value = false
  isEditIntent.value = false
  form.value = blank()
  resetUploadsAndGallery()
}

function clearInlineErrors() {
  projectNameError.value = ''
  locationError.value    = ''
  priceError.value       = ''
  descriptionError.value = ''
  paymentPlanError.value = ''
}

function resetUploadsAndGallery() {
  coverFile.value = null
  logoFile.value = null
  brochureFile.value = null
  queuedGallery.value = []
  galleryRows.value = []
}

function toNumberOrNull(v) { return v === '' || v === null || v === undefined ? null : Number(v) }
function normaliseNumbers() {
  form.value.min_price            = toNumberOrNull(form.value.min_price)
  form.value.max_price            = toNumberOrNull(form.value.max_price)
  form.value.down_payment         = toNumberOrNull(form.value.down_payment)
  form.value.land_area            = toNumberOrNull(form.value.land_area)
  form.value.project_buildup_area = toNumberOrNull(form.value.project_buildup_area)
  form.value.floors               = toNumberOrNull(form.value.floors)
}

function basename(path) {
  if (!path) return ''
  const i = path.lastIndexOf('/')
  return i >= 0 ? path.slice(i + 1) : path
}

/** Extract a human-readable message from Frappe server errors */
function serverMessage(e) {
  try {
    if (e?._server_messages) {
      const arr = JSON.parse(e._server_messages)
      if (Array.isArray(arr) && arr.length) {
        const msgs = arr.map(x => { try { return JSON.parse(x).message || x } catch { return x } })
        return msgs.join('\n')
      }
    }
  } catch {}
  // Translate well-known raw Frappe error class names into friendly messages
  const raw = String(e?.message || e?._error_message || e?.exc || '')
  if (raw.includes('CharacterLengthExceededError')) {
    return __('A field value exceeds the maximum allowed length. Please shorten the Project Name or Description.')
  }
  if (raw.includes('ValidationError')) {
    // Try to strip Python traceback, keep only the last meaningful line
    const lines = raw.split('\n').map(l => l.trim()).filter(Boolean)
    const last = lines[lines.length - 1]
    return last || __('Validation failed. Please check your inputs.')
  }
  if (e?.message) return e.message
  return __('Something went wrong. Please try again.')
}

function isValidURL(value) {
  if (!value) return true
  try {
    const u = new URL(value)
    return u.protocol === 'http:' || u.protocol === 'https:'
  } catch {
    return false
  }
}

/** Normalise furnishing to canonical casing before sending to server */
function canonicalFurnishing(raw) {
  if (!raw) return raw
  return FURNISHING_CANONICAL[raw.toLowerCase()] || raw
}

/* ---------- inline validators (on blur) ---------- */
function validateProjectName() {
  const name = (form.value.project_name || '').trim()
  if (!name) {
    projectNameError.value = __('Project Name is required.')
  } else if (name.length > PROJECT_NAME_MAX) {
    projectNameError.value = __('Project Name must not exceed {0} characters.', [PROJECT_NAME_MAX])
  } else {
    projectNameError.value = ''
  }
}

function validateLocation() {
  if (form.value.location && !isValidURL(form.value.location)) {
    locationError.value = __('Location must be a valid URL (e.g., https://maps.google.com/...)')
  } else {
    locationError.value = ''
  }
}

function validatePrices() {
  const min = toNumberOrNull(form.value.min_price)
  const max = toNumberOrNull(form.value.max_price)
  if (min !== null && max !== null && min > max) {
    priceError.value = __('Min Price cannot be greater than Max Price.')
  } else {
    priceError.value = ''
  }
}

/* ---------- meta loaders ---------- */
function parseSelectOptionsFromMetaField(f) {
  const opts = String(f.options || '')
    .split('\n')
    .map(s => s.trim())
    .filter(Boolean)
  return opts.map(v => ({ label: v, value: v }))
}

async function loadMetaAndDefaults() {
  try {
    const meta = await call('frappe.client.get_meta', { doctype: 'Real Estate Project' })
    metaFields.value = Array.isArray(meta?.fields) ? meta.fields : []

    const map = {}
    for (const f of metaFields.value) {
      if (f.fieldtype === 'Select') {
        const fromMeta = parseSelectOptionsFromMetaField(f)
        if (f.fieldname === 'status') {
          map[f.fieldname] = fromMeta.length ? fromMeta : FALLBACK_STATUS
        } else if (f.fieldname === 'categories') {
          map[f.fieldname] = fromMeta.length ? fromMeta : FALLBACK_CATEGORIES
        } else if (f.fieldname === 'exclusivity') {
          map[f.fieldname] = fromMeta.length ? fromMeta : FALLBACK_EXCLUSIVITY
        } else if (f.fieldname === 'furnishing') {
          map[f.fieldname] = fromMeta.length ? fromMeta : FALLBACK_FURNISHING
        } else {
          map[f.fieldname] = fromMeta
        }
      }
    }
    if (!map.status)      map.status      = FALLBACK_STATUS
    if (!map.categories)  map.categories  = FALLBACK_CATEGORIES
    if (!map.exclusivity) map.exclusivity = FALLBACK_EXCLUSIVITY
    if (!map.furnishing)  map.furnishing  = FALLBACK_FURNISHING
    selectOptionsMap.value = map

    // naming_series
    const ns = metaFields.value.find(f => f.fieldname === 'naming_series')
    hasNamingSeries.value = !!ns
    namingSeriesReqd.value = !!ns?.reqd
    namingSeriesOptions.value = ns
      ? String(ns.options || '').split('\n').map(s => s.trim()).filter(Boolean)
      : []

    form.value = applyMetaDefaults(form.value || blank())
  } catch {
    metaFields.value = []
    selectOptionsMap.value = {
      status:      FALLBACK_STATUS,
      categories:  FALLBACK_CATEGORIES,
      exclusivity: FALLBACK_EXCLUSIVITY,
      furnishing:  FALLBACK_FURNISHING,
    }
    hasNamingSeries.value = false
  }
}

function applyMetaDefaults(src) {
  const out = { ...src }
  if (hasNamingSeries.value && !out.naming_series && namingSeriesOptions.value.length) {
    out.naming_series = namingSeriesOptions.value[0]
  }
  // Normalise furnishing case on load
  if (out.furnishing) {
    out.furnishing = canonicalFurnishing(out.furnishing) || out.furnishing
  }
  return out
}

function setDefaultSelectsFromOptions() {
  const map = selectOptionsMap.value
  Object.keys(map).forEach((fname) => {
    if (!form.value[fname] && map[fname]?.length) {
      form.value[fname] = map[fname][0].value
    }
  })
}

/* ---------- fetch existing (edit) ---------- */
async function fetchAndBind(name) {
  loading.value = true
  try {
    const doc = await call('frappe.client.get', { doctype: 'Real Estate Project', name })
    form.value = applyMetaDefaults(Object.assign(blank(), doc))
    normalizeSelectsAgainstOptions()

    const rows = Array.isArray(doc?.gallery)
      ? doc.gallery.map(r => ({
          image: r.image || r.file || r.image_url,
          caption: r.caption || r.title || '',
        })).filter(r => r.image)
      : []
    galleryRows.value = rows
  } catch (e) {
    errorMsg.value = serverMessage(e) || __('Could not load project')
    form.value = applyMetaDefaults(Object.assign(blank(), { name }))
  } finally {
    loading.value = false
  }
}

/* ---------- file pickers ---------- */
function onCoverPicked(e) { const f = e.target?.files?.[0]; if (f) coverFile.value = f }
function clearCover()     { coverFile.value = null; form.value.cover_image = ''; if (coverInput.value) coverInput.value.value = '' }
function onLogoPicked(e)  { const f = e.target?.files?.[0]; if (f) logoFile.value = f }
function clearLogo()      { logoFile.value = null; form.value.logo = ''; if (logoInput.value) logoInput.value.value = '' }
function onBrochurePicked(e) { const f = e.target?.files?.[0]; if (f) brochureFile.value = f }
function clearBrochure()  { brochureFile.value = null; form.value.brochure = ''; if (brochureInput.value) brochureInput.value.value = '' }

/* ---------- gallery ---------- */
function onGalleryPicked(e) {
  const files = Array.from(e.target?.files || [])
  if (!files.length) return
  if (form.value.name) void addFilesToGallery(files)
  else queuedGallery.value.push(...files)
}

async function uploadFile({ doctype, docname, file }) {
  const fd = new FormData()
  fd.append('doctype', doctype)
  fd.append('docname', docname)
  fd.append('is_private', '0')
  fd.append('file', file)
  const headers = {}
  if (window.csrf_token) headers['X-Frappe-CSRF-Token'] = window.csrf_token
  const res = await fetch('/api/method/upload_file', {
    method: 'POST', headers, body: fd, credentials: 'same-origin',
  })
  const j = await res.json()
  const url = j?.message?.file_url
  if (!url) throw new Error(__('File upload failed. Please try again.'))
  return url
}

async function addFilesToGallery(files) {
  if (!form.value.name) return
  const urls = []
  for (const f of files) urls.push(await uploadFile({ doctype: 'Real Estate Project', docname: form.value.name, file: f }))

  for (const u of urls) {
    await call('frappe.client.insert', {
      doc: {
        doctype: 'Project Image',
        parent: form.value.name,
        parenttype: 'Real Estate Project',
        parentfield: 'gallery',
        image: u,
        caption: '',
      },
    })
  }

  const fresh = await call('frappe.client.get', { doctype: 'Real Estate Project', name: form.value.name })
  galleryRows.value = Array.isArray(fresh?.gallery)
    ? fresh.gallery.map(r => ({ image: r.image || r.file || r.image_url, caption: r.caption || '' })).filter(r => r.image)
    : []
}

/* ---------- safe save w/ timestamp retry ---------- */
async function safeSave(doc) {
  try {
    const gv = await call('frappe.client.get_value', {
      doctype: doc.doctype,
      filters: { name: doc.name },
      fieldname: 'modified',
    })
    if (gv?.modified) doc.modified = gv.modified
  } catch {}
  try {
    return await call('frappe.client.save', { doc })
  } catch (e) {
    const isTS = String(e.exc || e.message || '').includes('TimestampMismatchError')
    if (!isTS) throw e
    const fresh = await call('frappe.client.get', { doctype: doc.doctype, name: doc.name })
    return await call('frappe.client.save', { doc: { ...fresh, ...doc, modified: fresh.modified } })
  }
}

/* ---------- payloads ---------- */
const BASE_FIELDS = [
  'doctype', 'project_name', 'status', 'exclusivity', 'developer',
  'city', 'district', 'location', 'marketing_campaign',
  'min_price', 'max_price', 'land_area', 'project_buildup_area',
  'area', 'down_payment', 'floors', 'furnishing',
  'categories', 'payment_plan', 'description',
]

function pickInsert(src) {
  const keys = [...BASE_FIELDS]
  if (hasNamingSeries.value) keys.push('naming_series')
  const out = { doctype: 'Real Estate Project' }
  for (const k of keys) {
    const v = src[k]
    if (v !== undefined && v !== null && v !== '') out[k] = v
  }
  return out
}

function pickUpdate(src) {
  const keys = ['name', ...BASE_FIELDS]
  if (hasNamingSeries.value) keys.push('naming_series')
  const out = { doctype: 'Real Estate Project', name: src.name }
  for (const k of keys) {
    const v = src[k]
    if (v === undefined) continue
    out[k] = v ?? null
  }
  return out
}

/* ---------- required checks ---------- */
function requiredMissingIn(doc) {
  const missing = []
  for (const f of metaFields.value) {
    if (!f.reqd) continue
    const v = doc[f.fieldname]
    const empty = v === undefined || v === null || (typeof v === 'string' && v.trim() === '')
    if (empty) missing.push(f.label || f.fieldname)
  }
  return missing
}

/* ---------- select normalization ---------- */
function normalizeSelectsAgainstOptions() {
  const map = selectOptionsMap.value
  for (const [fname, arr] of Object.entries(map)) {
    const allowed = arr.map(o => o.value)
    const cur = form.value[fname]
    if (cur && !allowed.includes(cur)) {
      // Try canonical map first (for furnishing)
      const fixed = canonicalFurnishing(cur)
      form.value[fname] = allowed.includes(fixed) ? fixed : (allowed[0] || '')
    }
  }
}

/* ---------- full save validation ---------- */
function runClientValidation() {
  clearInlineErrors()
  let ok = true

  const name = (form.value.project_name || '').trim()
  if (!name) {
    projectNameError.value = __('Project Name is required.')
    ok = false
  } else if (name.length > PROJECT_NAME_MAX) {
    projectNameError.value = __('Project Name must not exceed {0} characters.', [PROJECT_NAME_MAX])
    ok = false
  }

  if (form.value.location && !isValidURL(form.value.location)) {
    locationError.value = __('Location must be a valid URL (e.g., https://maps.google.com/...).')
    ok = false
  }

  const min = toNumberOrNull(form.value.min_price)
  const max = toNumberOrNull(form.value.max_price)
  if (min !== null && max !== null && min > max) {
    priceError.value = __('Min Price cannot be greater than Max Price.')
    ok = false
  }

  const desc = form.value.description || ''
  if (desc.length > DESCRIPTION_MAX) {
    descriptionError.value = __('Description must not exceed {0} characters.', [DESCRIPTION_MAX])
    ok = false
  }

  const plan = form.value.payment_plan || ''
  if (plan.length > PAYMENT_PLAN_MAX) {
    paymentPlanError.value = __('Payment Plan must not exceed {0} characters.', [PAYMENT_PLAN_MAX])
    ok = false
  }

  const catOpts = selectOptions('categories')
  if (catOpts.length && !form.value.categories) {
    errorMsg.value = __('Categories is required.')
    ok = false
  }

  if (!form.value.status) {
    errorMsg.value = (errorMsg.value ? errorMsg.value + '\n' : '') + __('Status is required.')
    ok = false
  }

  if (hasNamingSeries.value && namingSeriesReqd.value && !form.value.naming_series) {
    errorMsg.value = (errorMsg.value ? errorMsg.value + '\n' : '') + __('Naming Series is required.')
    ok = false
  }

  return ok
}

/* ---------- save ---------- */
async function save() {
  errorMsg.value = ''

  // Run all client-side validations before any network call
  if (!runClientValidation()) {
    ref_project_name.value?.querySelector?.('input')?.focus?.()
    return
  }

  // Normalise furnishing case before sending
  if (form.value.furnishing) {
    form.value.furnishing = canonicalFurnishing(form.value.furnishing) || form.value.furnishing
  }

  normalizeSelectsAgainstOptions()
  normaliseNumbers()

  saving.value = true

  try {
    if (isEditIntent.value) {
      const fresh = await call('frappe.client.get', { doctype: 'Real Estate Project', name: form.value.name })
      const update = pickUpdate(form.value)
      const merged = { ...fresh, ...update, modified: fresh.modified }
      const miss = requiredMissingIn(merged)
      if (miss.length) {
        errorMsg.value = __('Missing required fields: {0}', [miss.join(', ')])
        saving.value = false
        return
      }
      await safeSave(merged)
    } else {
      const toInsert = pickInsert(form.value)
      const miss = requiredMissingIn(toInsert)
      if (miss.length) {
        errorMsg.value = __('Missing required fields: {0}', [miss.join(', ')])
        saving.value = false
        return
      }
      const inserted = await call('frappe.client.insert', { doc: toInsert })
      form.value.name = inserted?.name
    }

    if (form.value.name) {
      if (coverFile.value) {
        const url = await uploadFile({ doctype: 'Real Estate Project', docname: form.value.name, file: coverFile.value })
        form.value.cover_image = url
        await call('frappe.client.set_value', { doctype: 'Real Estate Project', name: form.value.name, fieldname: 'cover_image', value: url })
        try { URL.revokeObjectURL(coverPreviewSrc.value) } catch {}
        previewKey.value = Date.now()
      }
      if (logoFile.value) {
        const url = await uploadFile({ doctype: 'Real Estate Project', docname: form.value.name, file: logoFile.value })
        form.value.logo = url
        await call('frappe.client.set_value', { doctype: 'Real Estate Project', name: form.value.name, fieldname: 'logo', value: url })
        previewKey.value = Date.now()
      }
      if (brochureFile.value) {
        const url = await uploadFile({ doctype: 'Real Estate Project', docname: form.value.name, file: brochureFile.value })
        form.value.brochure = url
        await call('frappe.client.set_value', { doctype: 'Real Estate Project', name: form.value.name, fieldname: 'brochure', value: url })
      }
      if (queuedGallery.value.length) {
        await addFilesToGallery(queuedGallery.value)
        queuedGallery.value = []
      }
    }

    emit('saved')
    close()
  } catch (e) {
    console.error(e)
    errorMsg.value = serverMessage(e)
  } finally {
    saving.value = false
  }
}

/* expose showConfirm so parent (Inventory.vue) can call it for delete confirmation */
defineExpose({ showConfirm })
</script>