<template>
  <div v-if="leadData" class="flex flex-col gap-4 p-4 pt-0">
    <div class="flex items-center justify-end max-w-7xl mx-auto w-full py-0 mb-0">
      <Button
        variant="solid"
        :label="__('Save')"
        :loading="isSaving"
        :disabled="!props.docState?.isDirty"
        @click="saveLead"
      />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-7xl mx-auto w-full">
      <!-- Card 1: Location & Type -->
      <div class="bg-white border border-gray-100 rounded-xl shadow-sm p-6 flex flex-col h-full">
        <h3 class="text-lg font-bold text-gray-800 mb-6">{{ __('Location & Type') }}</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">

          <!-- Country toggle — spans full width -->
          <div class="sm:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ __('Country') }}</label>
            <div class="flex gap-3">
              <button
                v-for="country in ['Egypt', 'Saudi Arabia']"
                :key="country"
                @click="selectCountry(country)"
                :class="[
                  'flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border text-sm font-medium transition-all',
                  props.docState.doc.property_country === country
                    ? 'border-blue-500 bg-blue-50 text-blue-700 shadow-sm'
                    : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50'
                ]"
              >
                <span class="text-base">{{ country === 'Egypt' ? '🇪🇬' : '🇸🇦' }}</span>
                {{ __(country) }}
              </button>
            </div>
          </div>

          <!-- City Combobox -->
          <div class="relative">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ __('City') }}</label>
            <div class="relative">
              <input
                type="text"
                v-model="cityInput"
                @input="onCityInput"
                @focus="showCityDropdown = true"
                @blur="onCityBlur"
                @keydown.down.prevent="cityHighlight = Math.min(cityHighlight + 1, filteredCities.length - 1)"
                @keydown.up.prevent="cityHighlight = Math.max(cityHighlight - 1, 0)"
                @keydown.enter.prevent="selectCity(filteredCities[cityHighlight])"
                @keydown.escape="showCityDropdown = false"
                :placeholder="props.docState.doc.property_country ? __('Type or select a city...') : __('Select a country first')"
                class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <span
                v-if="cityInput"
                @mousedown.prevent="clearCity"
                class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 cursor-pointer text-lg leading-none"
              >×</span>
            </div>
            <ul
              v-if="showCityDropdown && filteredCities.length"
              class="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-56 overflow-y-auto text-sm"
            >
              <li
                v-for="(city, i) in filteredCities"
                :key="city"
                @mousedown.prevent="selectCity(city)"
                :class="[
                  'px-4 py-2 cursor-pointer hover:bg-blue-50 hover:text-blue-700 transition-colors',
                  i === cityHighlight ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                ]"
              >
                {{ city }}
              </li>
            </ul>
            <p v-if="showCityDropdown && cityInput && !filteredCities.length" class="text-xs text-gray-400 mt-1">
              {{ __('Custom value will be saved') }}
            </p>
          </div>

          <!-- Region Combobox -->
          <div class="relative">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ __('Region / District') }}</label>
            <div class="relative">
              <input
                type="text"
                v-model="regionInput"
                @input="onRegionInput"
                @focus="showRegionDropdown = true"
                @blur="onRegionBlur"
                @keydown.down.prevent="regionHighlight = Math.min(regionHighlight + 1, filteredRegions.length - 1)"
                @keydown.up.prevent="regionHighlight = Math.max(regionHighlight - 1, 0)"
                @keydown.enter.prevent="selectRegion(filteredRegions[regionHighlight])"
                @keydown.escape="showRegionDropdown = false"
                :placeholder="props.docState.doc.property_city ? __('Type or select a district...') : __('Select a city first')"
                class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <span
                v-if="regionInput"
                @mousedown.prevent="clearRegion"
                class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 cursor-pointer text-lg leading-none"
              >×</span>
            </div>
            <ul
              v-if="showRegionDropdown && filteredRegions.length"
              class="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-56 overflow-y-auto text-sm"
            >
              <li
                v-for="(region, i) in filteredRegions"
                :key="region"
                @mousedown.prevent="selectRegion(region)"
                :class="[
                  'px-4 py-2 cursor-pointer hover:bg-blue-50 hover:text-blue-700 transition-colors',
                  i === regionHighlight ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                ]"
              >
                {{ region }}
              </li>
            </ul>
            <p v-if="showRegionDropdown && regionInput && !filteredRegions.length" class="text-xs text-gray-400 mt-1">
              {{ __('Custom value will be saved') }}
            </p>
          </div>

          <div v-for="fieldName in card1RemainingFieldNames" :key="fieldName">
            <Field v-if="getField(fieldName)" :field="getField(fieldName)" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ __('Project Name') }}</label>
            <FormControl
              v-if="props.docState.doc.property_relation === 'Project'"
              type="select"
              v-model="props.docState.doc.property_project"
              :options="projectOptions"
              :placeholder="projects.data?.length ? __('Select project') : __('No results found')"
            />
            <FormControl
              v-else
              type="text"
              :modelValue="props.docState.doc.property_project || ''"
              disabled
            />
            <p
              v-if="props.docState.doc.property_relation !== 'Project'"
              class="text-xs text-gray-500 mt-1"
            >
              {{ __('Filled when Property Relation = Project') }}
            </p>
          </div>
        </div>
      </div>

      <!-- Card 2: Property Details -->
      <div class="bg-white border border-gray-100 rounded-xl shadow-sm p-6 flex flex-col h-full">
        <h3 class="text-lg font-bold text-gray-800 mb-6">{{ __('Property Details') }}</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ __('Property Space (sqm)') }}</label>
            <FormControl type="number" v-model="props.docState.doc.property_space" />
          </div>

          <div v-if="getField('property_floor')">
            <Field :field="getField('property_floor')" />
          </div>

          <div v-if="getField('property_bedrooms')">
            <Field :field="getField('property_bedrooms')" />
          </div>

          <div v-if="getField('property_bathrooms')">
            <Field :field="getField('property_bathrooms')" />
          </div>

          <div v-if="getField('property_condition')">
            <Field :field="getField('property_condition')" />
          </div>

          <div v-if="getField('property_decoration')">
            <Field :field="getField('property_decoration')" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ __('Year Built') }}</label>
            <FormControl type="number" v-model="props.docState.doc.property_year_built" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ __('Expected Delivery Date') }}</label>
            <FormControl type="date" v-model="props.docState.doc.property_delivery_date" />
          </div>
        </div>
      </div>

      <!-- Card 3: Features & Financial -->
      <div class="bg-white border border-gray-100 rounded-xl shadow-sm p-6 flex flex-col h-full">
        <h3 class="text-lg font-bold text-gray-800 mb-6">{{ __('Features & Financial') }}</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div v-if="getField('property_view')">
            <Field :field="getField('property_view')" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ __('Finishing Level') }}</label>
            <FormControl type="text" v-model="props.docState.doc.property_finishing" />
          </div>

          <div v-if="getField('property_features')">
            <Field :field="getField('property_features')" />
          </div>

          <!-- Min Budget with currency badge -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              {{ __('Min Budget') }}
              <span
                class="ml-1.5 px-1.5 py-0.5 rounded text-xs font-semibold"
                :class="currencyBadgeClass"
              >{{ currency }}</span>
            </label>
            <FormControl type="number" v-model="props.docState.doc.property_min_price" />
          </div>

          <!-- Max Budget with currency badge -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              {{ __('Max Budget') }}
              <span
                class="ml-1.5 px-1.5 py-0.5 rounded text-xs font-semibold"
                :class="currencyBadgeClass"
              >{{ currency }}</span>
            </label>
            <FormControl type="number" v-model="props.docState.doc.property_max_price" />
          </div>

          <div v-if="getField('property_payment')">
            <Field :field="getField('property_payment')" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ __('Down Payment (%)') }}</label>
            <FormControl type="number" v-model="props.docState.doc.property_down_payment" />
          </div>

          <div v-if="getField('property_ownership')">
            <Field :field="getField('property_ownership')" />
          </div>
        </div>
      </div>

      <!-- Card 4: Slideable Notes -->
      <div class="bg-white border border-gray-100 rounded-xl shadow-sm p-6 flex flex-col h-full overflow-hidden">
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center gap-2">
            <h3 class="text-lg font-bold text-gray-800">{{ __('Notes') }}</h3>
            <span v-if="notes.length > 1" class="text-xs text-gray-400 font-medium">
              ({{ currentNoteIndex + 1 }} / {{ notes.length }})
            </span>
          </div>

          <div class="flex items-center gap-2">
            <template v-if="notes.length > 1">
              <Button variant="ghost" @click="prevNote" :disabled="currentNoteIndex === 0">
                <template #icon>
                  <FeatherIcon name="chevron-left" class="h-5 w-5" />
                </template>
              </Button>
              <Button variant="ghost" @click="nextNote" :disabled="currentNoteIndex === notes.length - 1">
                <template #icon>
                  <FeatherIcon name="chevron-right" class="h-5 w-5" />
                </template>
              </Button>
            </template>

            <Button variant="ghost" class="hover:bg-gray-50" @click="showCreateNoteModal = true">
              <template #icon>
                <FeatherIcon name="plus" class="h-6 w-6 text-blue-500" />
              </template>
            </Button>

            <Button v-if="currentNote" variant="ghost" class="hover:bg-red-50" @click="confirmDeleteNote">
              <template #icon>
                <FeatherIcon name="trash-2" class="h-5 w-5 text-red-500" />
              </template>
            </Button>
          </div>
        </div>

        <div v-if="currentNote" class="bg-gray-50 rounded-xl p-5 flex-1 flex flex-col transition-all duration-300">
          <div class="text-[15px] text-gray-700 leading-relaxed overflow-y-auto flex-1 mb-4 scrollbar-hide">
            <div class="font-bold text-sm text-gray-800 mb-2" v-if="currentNote.title">
              {{ currentNote.title }}
            </div>
            <div v-html="currentNote.content" class="prose prose-sm max-w-none"></div>
          </div>
          <div class="flex items-center justify-between text-[11px] text-gray-400 border-t border-gray-200/60 pt-3 mt-auto shrink-0 font-medium">
            <div class="flex items-center gap-1.5">
              <span class="opacity-70">{{ __('Date:') }}</span>
              <span class="text-gray-500">{{ formatDate(currentNote.creation) }}</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="opacity-70">{{ __('Agent:') }}</span>
              <span class="text-gray-500">{{ currentNote.owner_name }}</span>
            </div>
          </div>
        </div>

        <div v-else class="flex flex-col items-center justify-center flex-1 text-gray-400 py-10">
          <NoteIcon class="h-10 w-10 opacity-10 mb-2" />
          <span class="text-sm italic opacity-60">{{ __('No notes added yet') }}</span>
        </div>
      </div>
    </div>

    <!-- Note Creation Modal -->
    <Dialog v-model="showCreateNoteModal" :options="{ title: __('Add Note'), size: 'sm' }">
      <template #body-content>
        <div class="p-4 space-y-4">
          <FormControl type="text" :placeholder="__('Title')" v-model="newNote.title" />
          <FormControl type="textarea" :placeholder="__('Note content...')" v-model="newNote.content" rows="6" />
        </div>
      </template>
      <template #actions>
        <Button variant="solid" :label="__('Add Note')" :loading="savingNote" @click="addNote" />
        <Button variant="ghost" :label="__('Cancel')" @click="showCreateNoteModal = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, provide, watch } from 'vue'
import { call, Button, Dialog, FormControl, toast, FeatherIcon, createResource } from 'frappe-ui'
import { formatDate } from '@/utils'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import Field from '@/components/FieldLayout/Field.vue'
import { usersStore } from '@/stores/users'
import { getMeta } from '@/stores/meta'

const emit = defineEmits(['saved', 'dirty'])

const props = defineProps({
  leadData: Object,
  docname: String,
  docState: {
    type: Object,
    required: true,
  },
})

// ─── Location Data: Country → City → Region ───────────────────────────────────

const COUNTRY_CITIES = {
  'Egypt': [
    'Cairo', 'New Cairo', 'Nasr City', 'Heliopolis', 'Maadi',
    '6th of October', 'Sheikh Zayed', 'Zamalek', 'New Administrative Capital',
    'Al Shorouk City', 'Al Obour City', 'Alexandria', 'Giza',
    'North Coast', 'Ain Sokhna', 'El Gouna', 'Hurghada', 'Sharm El Sheikh',
  ],
  'Saudi Arabia': [
    'Riyadh', 'Jeddah', 'Makkah', 'Madinah', 'Dammam',
    'Khobar', 'Dhahran', 'Abha', 'Tabuk', 'Yanbu',
    'Najran', 'Hail', 'Al Khobar', 'Jubail',
  ],
}

const CITY_REGIONS = {
  // ── Egypt ──
  'Cairo': [
    'Downtown Cairo', 'Garden City', 'Zamalek', 'Heliopolis', 'Nasr City',
    'Madinet Nasr', 'Shoubra', 'Shubra El Kheima', 'Mohandessin', 'Agouza', 'Dokki',
  ],
  'New Cairo': [
    'New Cairo - 1st Settlement', 'New Cairo - 3rd Settlement', 'New Cairo - 5th Settlement',
    'Beit El Watan', 'Al Rehab City', 'Madinaty', 'Mostakbal City',
  ],
  'Nasr City': ['Madinet Nasr', 'Nasr City'],
  'Heliopolis': ['Heliopolis', 'Korba', 'Al Nozha', 'Al Merghany'],
  'Maadi': ['Maadi', 'Degla', 'Sarayat', 'Zohour', 'New Maadi'],
  '6th of October': ['6th of October - Hay 1', '6th of October - Hay 2', '6th of October - Hay 3'],
  'Sheikh Zayed': ['Sheikh Zayed - Hay 1', 'Sheikh Zayed - Hay 2'],
  'Zamalek': ['Zamalek'],
  'New Administrative Capital': [
    'New Administrative Capital - R1',
    'New Administrative Capital - R2',
    'New Administrative Capital - R3',
  ],
  'Al Shorouk City': ['Al Shorouk City'],
  'Al Obour City': ['Al Obour City'],
  'Alexandria': ['Smouha', 'Gleem', 'San Stefano', 'Sidi Bishr', 'Miami', 'Agami', 'Borg El Arab'],
  'Giza': ['Giza', 'Dokki', 'Agouza', 'Mohandessin', 'Faisal', 'Haram'],
  'North Coast': ['Sahel', 'Marassi', 'Hacienda Bay', 'Sidi Abdel Rahman', 'Marina'],
  'Ain Sokhna': ['Ain Sokhna'],
  'El Gouna': ['El Gouna'],
  'Hurghada': ['Hurghada'],
  'Sharm El Sheikh': ['Sharm El Sheikh'],
  // ── Saudi Arabia ──
  'Riyadh': [
    'Al Malaz', 'Al Muruj', 'Al Olaya', 'Al Sulaimaniyah', 'Al Rawdah',
    'Al Narjis', 'Al Yasmin', 'Al Qirawan', 'Hittin', 'Al Sahafah',
    'Al Nakheel', 'Al Aqiq', 'Diplomatic Quarter', 'King Abdullah District',
  ],
  'Jeddah': [
    'Al Hamra', 'Al Rawdah', 'Al Zahraa', 'Al Shati', 'Al Naim',
    'Al Marwah', 'Al Salamah', 'Al Faisaliyah', 'Al Balad', 'Al Khalidiyah',
    'Al Aziziyah', 'Al Safa', 'Al Rehab', 'Al Bawadi',
  ],
  'Makkah': ['Al Aziziyah', 'Al Zaher', 'Al Adl', 'Ajyad', 'Al Naseem'],
  'Madinah': ['Al Haram', 'Al Awali', 'Quba', 'Al Anbariyah'],
  'Dammam': ['Al Faisaliyah', 'Al Shula', 'Al Badiyah', 'Al Noor', 'Al Nur'],
  'Khobar': ['Al Thuqbah', 'Al Aqrabiyah', 'Al Ulaya', 'Al Corniche'],
  'Dhahran': ['Dhahran'],
  'Abha': ['Al Manhal', 'Al Wurood', 'Abha Al Jadeedah'],
  'Tabuk': ['Tabuk'],
  'Yanbu': ['Yanbu'],
  'Najran': ['Najran'],
  'Hail': ['Hail'],
  'Al Khobar': ['Al Khobar'],
  'Jubail': ['Jubail Industrial City', 'Al Jubail'],
}

// ─── Currency ─────────────────────────────────────────────────────────────────

const currency = computed(() =>
  props.docState?.doc?.property_country === 'Saudi Arabia' ? 'SAR' : 'EGP'
)

const currencyBadgeClass = computed(() =>
  props.docState?.doc?.property_country === 'Saudi Arabia'
    ? 'bg-green-100 text-green-700'
    : 'bg-blue-100 text-blue-700'
)

// ─── Combobox State ───────────────────────────────────────────────────────────

const cityInput = ref('')
const showCityDropdown = ref(false)
const cityHighlight = ref(0)

const regionInput = ref('')
const showRegionDropdown = ref(false)
const regionHighlight = ref(0)

// Cities: filtered by selected country first, then by typed text
const filteredCities = computed(() => {
  const country = props.docState?.doc?.property_country || ''
  const base = country
    ? (COUNTRY_CITIES[country] || [])
    : Object.values(COUNTRY_CITIES).flat()
  const q = cityInput.value.toLowerCase().trim()
  return q ? base.filter(c => c.toLowerCase().includes(q)) : base
})

// Regions: filtered by selected city, then by typed text
const regionsForCity = computed(() => {
  const city = props.docState?.doc?.property_city || ''
  if (CITY_REGIONS[city]) return CITY_REGIONS[city]
  const match = Object.keys(CITY_REGIONS).find(k =>
    k.toLowerCase().includes(city.toLowerCase()) ||
    city.toLowerCase().includes(k.toLowerCase())
  )
  return match ? CITY_REGIONS[match] : []
})

const filteredRegions = computed(() => {
  const q = regionInput.value.toLowerCase().trim()
  const base = regionsForCity.value.length
    ? regionsForCity.value
    : Object.values(CITY_REGIONS).flat()
  const unique = [...new Set(base)]
  return q ? unique.filter(r => r.toLowerCase().includes(q)) : unique
})

function syncInputsFromDoc() {
  cityInput.value = props.docState?.doc?.property_city || ''
  regionInput.value = props.docState?.doc?.property_region || ''
}

// ─── Country handler ──────────────────────────────────────────────────────────

function selectCountry(country) {
  // Click same country again → deselect
  if (props.docState.doc.property_country === country) {
    props.docState.doc.property_country = ''
  } else {
    props.docState.doc.property_country = country
  }
  // Cascade clear city + region
  cityInput.value = ''
  props.docState.doc.property_city = ''
  regionInput.value = ''
  props.docState.doc.property_region = ''
}

// ─── City handlers ────────────────────────────────────────────────────────────

function onCityInput() {
  props.docState.doc.property_city = cityInput.value
  cityHighlight.value = 0
  showCityDropdown.value = true
  // Cascade clear region
  regionInput.value = ''
  props.docState.doc.property_region = ''
}

function selectCity(city) {
  if (!city) return
  cityInput.value = city
  props.docState.doc.property_city = city
  showCityDropdown.value = false
  regionInput.value = ''
  props.docState.doc.property_region = ''
}

function clearCity() {
  cityInput.value = ''
  props.docState.doc.property_city = ''
  regionInput.value = ''
  props.docState.doc.property_region = ''
}

function onCityBlur() {
  setTimeout(() => {
    showCityDropdown.value = false
    props.docState.doc.property_city = cityInput.value
  }, 150)
}

// ─── Region handlers ──────────────────────────────────────────────────────────

function onRegionInput() {
  props.docState.doc.property_region = regionInput.value
  regionHighlight.value = 0
  showRegionDropdown.value = true
}

function selectRegion(region) {
  if (!region) return
  regionInput.value = region
  props.docState.doc.property_region = region
  showRegionDropdown.value = false
}

function clearRegion() {
  regionInput.value = ''
  props.docState.doc.property_region = ''
}

function onRegionBlur() {
  setTimeout(() => {
    showRegionDropdown.value = false
    props.docState.doc.property_region = regionInput.value
  }, 150)
}

// ─── Rest of component ────────────────────────────────────────────────────────

const showCreateNoteModal = ref(false)
const savingNote = ref(false)
const isSaving = ref(false)
const notes = ref([])
const currentNoteIndex = ref(0)

const card1RemainingFieldNames = ['property_type', 'property_subtype', 'property_relation']

const { getUser } = usersStore()
const { doctypeMeta } = getMeta('CRM Lead')
const fieldsArr = computed(() => doctypeMeta['CRM Lead']?.fields || [])

function getField(fieldname) {
  return fieldsArr.value.find((f) => f.fieldname === fieldname)
}

provide('data', computed(() => props.docState?.doc || {}))
provide('doctype', 'CRM Lead')
provide('preview', ref(false))
provide('isGridRow', ref(false))

const currentNote = computed(() => notes.value[currentNoteIndex.value] || null)

const allowedFields = computed(() => [
  'property_country',
  'property_city',
  'property_region',
  ...card1RemainingFieldNames,
  'property_project',
  'property_space',
  'property_floor',
  'property_bedrooms',
  'property_bathrooms',
  'property_condition',
  'property_decoration',
  'property_year_built',
  'property_delivery_date',
  'property_view',
  'property_finishing',
  'property_features',
  'property_min_price',
  'property_max_price',
  'property_payment',
  'property_down_payment',
  'property_ownership',
])

const hasChanges = computed(() => {
  if (!props.docState?.doc || !props.docState?.originalDoc) return false
  return allowedFields.value.some(
    (key) => JSON.stringify(props.docState.doc[key]) !== JSON.stringify(props.docState.originalDoc[key])
  )
})

watch(hasChanges, (val) => {
  props.docState.isDirty = val
  if (val) emit('dirty')
}, { immediate: true })

watch(
  () => allowedFields.value.map((key) => props.docState?.doc?.[key]),
  () => {
    const dirty = hasChanges.value
    props.docState.isDirty = dirty
    if (dirty) emit('dirty')
  },
  { deep: true }
)

const projects = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Real Estate Project',
    fields: ['name', 'project_name'],
    limit_page_length: 999,
    order_by: 'project_name asc',
  },
  auto: true,
})

const projectOptions = computed(() =>
  (projects.data || []).map((p) => ({
    label: p.project_name || p.name,
    value: p.name,
  }))
)

const newNote = reactive({ title: '', content: '' })

async function fetchNotes() {
  try {
    const res = await call('crm.api.activities.get_activities', { name: props.docname })
    const notesData = res[2] || []
    notes.value = notesData
      .sort((a, b) => new Date(b.creation) - new Date(a.creation))
      .map((n) => ({
        ...n,
        owner_name: getUser(n.owner)?.full_name || n.owner,
      }))
    currentNoteIndex.value = 0
  } catch (e) {
    console.error('Failed to fetch notes', e)
  }
}

function nextNote() {
  if (currentNoteIndex.value < notes.value.length - 1) currentNoteIndex.value++
}

function prevNote() {
  if (currentNoteIndex.value > 0) currentNoteIndex.value--
}

async function addNote() {
  if (!newNote.content.trim()) return
  savingNote.value = true
  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: 'FCRM Note',
        title: newNote.title || 'Note',
        content: newNote.content,
        reference_doctype: 'CRM Lead',
        reference_docname: props.docname,
      },
    })
    newNote.title = ''
    newNote.content = ''
    showCreateNoteModal.value = false
    toast.success(__('Note added'))
    await fetchNotes()
  } catch (e) {
    toast.error(__('Failed to add note'))
  } finally {
    savingNote.value = false
  }
}

onMounted(() => {
  if (props.leadData && !props.docState?.originalDoc) {
    props.docState.originalDoc = JSON.parse(JSON.stringify(props.leadData))
  }
  syncInputsFromDoc()
  fetchNotes()
})

async function saveLead() {
  if (!props.docState?.doc || !props.docState?.originalDoc) {
    toast.error(__('Lead data not loaded'))
    return
  }

  const updatedDoc = props.docState.doc
  const oldDoc = props.docState.originalDoc

  if (updatedDoc.property_relation === 'Project') {
    if (!updatedDoc.property_project) {
      toast.error(__('Project Name is required when Property Relation is Project'))
      return
    }
    const validProjectNames = (projects.data || []).map((p) => p.name)
    if (!validProjectNames.includes(updatedDoc.property_project)) {
      toast.error(__('Please select a valid project from the list'))
      return
    }
  }

  const changes = allowedFields.value.reduce((acc, key) => {
    if (JSON.stringify(updatedDoc[key]) !== JSON.stringify(oldDoc[key])) {
      acc[key] = updatedDoc[key]
    }
    return acc
  }, {})

  if (!Object.keys(changes).length) {
    toast.info(__('No changes to save'))
    props.docState.isDirty = false
    return
  }

  isSaving.value = true
  try {
    await call('crm.api.doc.update_doc_fields', {
      doctype: 'CRM Lead',
      name: props.docname,
      fieldname: changes,
    })
    toast.success(__('Changes saved successfully'))
    Object.assign(props.docState.originalDoc, changes)
    props.docState.isDirty = false
    emit('saved', changes)
  } catch (err) {
    console.error('Property Preference save failed:', err)
    const msg = err?.messages?.[0] || err?.message || __('Failed to save changes')
    toast.error(msg)
  } finally {
    isSaving.value = false
  }
}

function confirmDeleteNote() {
  if (!currentNote.value) return
  if (confirm(__('Are you sure you want to delete this note?'))) deleteNote()
}

async function deleteNote() {
  if (!currentNote.value) return
  try {
    await call('frappe.client.delete', { doctype: 'FCRM Note', name: currentNote.value.name })
    toast.success(__('Note deleted'))
    await fetchNotes()
  } catch (e) {
    toast.error(__('Failed to delete note'))
  }
}

watch(() => props.docname, () => {
  syncInputsFromDoc()
  fetchNotes()
})
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>