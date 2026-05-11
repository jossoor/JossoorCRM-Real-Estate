<template>
  <Dialog v-model="show" :options="{ size: '4xl' }">
    <template #body>
      <div class="flex flex-col p-6 gap-8 bg-white rounded-xl max-h-[90vh] overflow-y-auto">

        <!-- ── Header ── -->
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-gray-800">{{ __('Add New Lead') }}</h2>
            <p class="text-sm text-gray-400 mt-0.5">{{ __('Fill in the details below to create a new lead') }}</p>
          </div>
          <button @click="show = false"
            class="w-9 h-9 flex items-center justify-center rounded-full bg-[#4A90E2] hover:bg-[#3B7DCC] transition-colors text-white text-lg font-bold shadow">
            ×
          </button>
        </div>

        <!-- ══════════════════════════════════════════════
             SECTION 1 — Lead Information
        ══════════════════════════════════════════════ -->
        <section>
          <SectionHeader :title="__('Lead Information')" />

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-4 mt-6">

            <FieldWrap :label="__('Title')">
              <SelectField v-model="lead.doc.salutation"
                :options="salutations.data?.map(s => s.name) ?? []"
                placeholder="" />
            </FieldWrap>

            <FieldWrap :label="__('First Name')" required>
              <input v-model.trim="lead.doc.first_name" type="text" class="fi" maxlength="50"
                :class="{ 'border-red-400 bg-red-50': fieldError === 'first_name' }" />
            </FieldWrap>

            <FieldWrap :label="__('Last Name')">
              <input v-model="lead.doc.last_name" type="text" class="fi" maxlength="140"
                :class="{ 'border-red-400 bg-red-50': fieldError === 'last_name' }" />
            </FieldWrap>

            <FieldWrap :label="__('Gender')" required>
              <div class="flex gap-4 h-10 items-center rounded-lg px-2"
                :class="{ 'border border-red-400 bg-red-50': fieldError === 'gender' }">
                <RadioBtn v-model="lead.doc.gender" value="Male"   :label="__('Male')"   name="gender" />
                <RadioBtn v-model="lead.doc.gender" value="Female" :label="__('Female')" name="gender" />
              </div>
            </FieldWrap>

            <FieldWrap :label="__('Email')">
              <input v-model="lead.doc.email" type="email" class="fi" maxlength="140"
                :class="{ 'border-red-400 bg-red-50': fieldError === 'email' }" />
            </FieldWrap>

            <!-- Mobile — accepts Egypt & Saudi -->
            <FieldWrap :label="__('Mobile No')" required>
              <input v-model="lead.doc.mobile_no" type="tel" class="fi" maxlength="20"
                :placeholder="__('01xxxxxxxxx or 05xxxxxxxx')"
                :class="{ 'border-red-400 bg-red-50': fieldError === 'mobile_no' }" />
            </FieldWrap>

            <!-- Other phone — accepts Egypt & Saudi -->
            <FieldWrap :label="__('Other Phone')">
              <input v-model="lead.doc.phone" type="tel" class="fi" maxlength="20"
                :placeholder="__('Optional')"
                :class="{ 'border-red-400 bg-red-50': fieldError === 'phone' }" />
            </FieldWrap>

            <FieldWrap :label="__('Source')">
              <SelectField v-model="lead.doc.source"
                :options="leadSources.data?.map(s => s.name) ?? []"
                placeholder="" />
            </FieldWrap>

            <FieldWrap :label="__('Territory')">
              <SelectField v-model="lead.doc.territory"
                :options="territories.data?.map(t => t.name) ?? []"
                placeholder="" />
            </FieldWrap>

            <FieldWrap :label="__('Industry')">
              <SelectField v-model="lead.doc.industry"
                :options="industries.data?.map(i => i.name) ?? []"
                placeholder="" />
            </FieldWrap>

            <FieldWrap :label="__('Lead Type')">
              <div class="flex gap-4 h-10 items-center">
                <RadioBtn v-for="opt in OPT.lead_type" :key="opt"
                  v-model="lead.doc.lead_type" :value="opt" :label="__(opt)" name="lead_type" />
              </div>
            </FieldWrap>

            <FieldWrap :label="__('Lead Owner')">
              <input v-model="lead.doc.lead_owner" type="text"
                class="fi bg-gray-50 text-gray-400 cursor-not-allowed"
                disabled />
            </FieldWrap>

          </div>

          <!-- Unit Assignment -->
          <div class="mt-4 pt-4 border-t border-gray-100">
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-3">
              {{ __('Unit Assignment') }}
            </p>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-x-6 gap-y-4">
              <FieldWrap :label="__('Project')">
                <SelectField
                  v-model="lead.doc.project"
                  :options="projects.data?.map(p => ({ value: p.name, label: p.project_name || p.name })) ?? []"
                  placeholder=""
                  @update:modelValue="onLeadProjectChange"
                />
              </FieldWrap>
              <FieldWrap :label="__('Project Unit')">
                <SelectField
                  v-model="lead.doc.project_unit"
                  :options="filteredProjectUnits.map(u => ({ value: u.name, label: u.unit_name || u.name }))"
                  :placeholder="!lead.doc.project ? __('Select project first') : __('Select unit')"
                  :disabled="!lead.doc.project"
                />
              </FieldWrap>
              <FieldWrap :label="__('Single Unit')">
                <SelectField
                  v-model="lead.doc.single_unit"
                  :options="units.data?.map(u => ({ value: u.name, label: u.unit_name || u.name })) ?? []"
                  placeholder=""
                />
              </FieldWrap>
            </div>
          </div>
        </section>

        <!-- ══════════════════════════════════════════════
             SECTION 2 — Property Preference
        ══════════════════════════════════════════════ -->
        <section>
          <SectionHeader :title="__('Property Preference')" />

          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">

            <!-- ── Card: Core Preference ── -->
            <PropCard :title="__('Core Preference')">

              <!-- Country toggle -->
              <FieldWrap :label="__('Country')">
                <div class="flex gap-2">
                  <button
                    v-for="country in ['Egypt', 'Saudi Arabia']"
                    :key="country"
                    type="button"
                    @click="selectCountry(country)"
                    :class="[
                      'flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg border text-xs font-semibold transition-all',
                      lead.doc.property_country === country
                        ? 'border-[#4A90E2] bg-[#4A90E2]/10 text-[#4A90E2]'
                        : 'border-gray-200 text-gray-500 hover:border-gray-300'
                    ]"
                  >
                    <span>{{ country === 'Egypt' ? '🇪🇬' : '🇸🇦' }}</span>
                    {{ __(country) }}
                  </button>
                </div>
              </FieldWrap>

              <!-- City combobox -->
              <FieldWrap :label="__('City')">
                <div class="relative">
                  <input
                    v-model="cityInput"
                    type="text"
                    class="fi"
                    maxlength="140"
                    :placeholder="lead.doc.property_country ? __('Type or select...') : __('Select country first')"
                    :class="{ 'border-red-400 bg-red-50': fieldError === 'property_city' }"
                    @input="onCityInput"
                    @focus="showCityDrop = true"
                    @blur="onCityBlur"
                    @keydown.down.prevent="cityHi = Math.min(cityHi + 1, filteredCities.length - 1)"
                    @keydown.up.prevent="cityHi = Math.max(cityHi - 1, 0)"
                    @keydown.enter.prevent="pickCity(filteredCities[cityHi])"
                    @keydown.escape="showCityDrop = false"
                  />
                  <span v-if="cityInput" @mousedown.prevent="clearCity"
                    class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 cursor-pointer text-lg leading-none">×</span>
                  <ul v-if="showCityDrop && filteredCities.length"
                    class="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto text-sm">
                    <li v-for="(city, i) in filteredCities" :key="city"
                      @mousedown.prevent="pickCity(city)"
                      :class="['px-3 py-2 cursor-pointer hover:bg-blue-50 hover:text-[#4A90E2]', i === cityHi ? 'bg-blue-50 text-[#4A90E2]' : 'text-gray-700']">
                      {{ city }}
                    </li>
                  </ul>
                  <p v-if="showCityDrop && cityInput && !filteredCities.length" class="text-xs text-gray-400 mt-1">
                    {{ __('Custom value will be saved') }}
                  </p>
                </div>
              </FieldWrap>

              <!-- Region combobox -->
              <FieldWrap :label="__('Region / District')">
                <div class="relative">
                  <input
                    v-model="regionInput"
                    type="text"
                    class="fi"
                    maxlength="140"
                    :placeholder="lead.doc.property_city ? __('Type or select...') : __('Select city first')"
                    :class="{ 'border-red-400 bg-red-50': fieldError === 'property_region' }"
                    @input="onRegionInput"
                    @focus="showRegionDrop = true"
                    @blur="onRegionBlur"
                    @keydown.down.prevent="regionHi = Math.min(regionHi + 1, filteredRegions.length - 1)"
                    @keydown.up.prevent="regionHi = Math.max(regionHi - 1, 0)"
                    @keydown.enter.prevent="pickRegion(filteredRegions[regionHi])"
                    @keydown.escape="showRegionDrop = false"
                  />
                  <span v-if="regionInput" @mousedown.prevent="clearRegion"
                    class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 cursor-pointer text-lg leading-none">×</span>
                  <ul v-if="showRegionDrop && filteredRegions.length"
                    class="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto text-sm">
                    <li v-for="(region, i) in filteredRegions" :key="region"
                      @mousedown.prevent="pickRegion(region)"
                      :class="['px-3 py-2 cursor-pointer hover:bg-blue-50 hover:text-[#4A90E2]', i === regionHi ? 'bg-blue-50 text-[#4A90E2]' : 'text-gray-700']">
                      {{ region }}
                    </li>
                  </ul>
                  <p v-if="showRegionDrop && regionInput && !filteredRegions.length" class="text-xs text-gray-400 mt-1">
                    {{ __('Custom value will be saved') }}
                  </p>
                </div>
              </FieldWrap>

              <FieldWrap :label="__('Property Type')">
                <div class="flex gap-2 flex-wrap">
                  <TypeChip v-for="t in OPT.property_type" :key="t"
                    v-model="lead.doc.property_type" :value="t" :label="__(t)"
                    @update:modelValue="lead.doc.property_subtype = ''" />
                </div>
              </FieldWrap>

              <FieldWrap :label="__('Property Subtype')">
                <SelectField
                  v-model="lead.doc.property_subtype"
                  :options="currentSubtypes"
                  :placeholder="lead.doc.property_type ? '' : __('Select a type first')"
                  :disabled="!lead.doc.property_type"
                />
              </FieldWrap>

              <FieldWrap :label="__('Space (sqm)')">
                <div :class="fieldError === 'property_space' ? 'border border-red-400 bg-red-50 rounded-lg p-2' : ''">
                  <Slider v-model="lead.doc.property_space"
                    :max="SPACE_MAX" :format="v => v + ' m²'" />
                </div>
              </FieldWrap>

              <FieldWrap :label="__('Floor Preference')">
                <SelectField v-model="lead.doc.property_floor"
                  :options="OPT.property_floor" placeholder="" />
              </FieldWrap>

            </PropCard>

            <!-- ── Card: Property Details ── -->
            <PropCard :title="__('Property Details')">

              <FieldWrap :label="__('Condition')">
                <div class="flex flex-col gap-1.5">
                  <RadioBtn v-for="c in OPT.property_condition" :key="c"
                    v-model="lead.doc.property_condition" :value="c" :label="__(c)" name="condition" />
                </div>
              </FieldWrap>

              <FieldWrap :label="__('Decoration Status')">
                <SelectField v-model="lead.doc.property_decoration"
                  :options="OPT.property_decoration" placeholder="" />
              </FieldWrap>

              <FieldWrap :label="__('Finishing Level')">
                <SelectField
                  v-model="lead.doc.property_finishing"
                  :options="currentFinishingOptions"
                  :placeholder="__('Select finishing level')"
                />
              </FieldWrap>

              <FieldWrap :label="__('Property Relation')">
                <div class="flex gap-2 flex-wrap mb-2">
                  <TypeChip
                    v-for="r in OPT.property_relation" :key="r"
                    v-model="lead.doc.property_relation" :value="r" :label="__(r)"
                    @update:modelValue="v => { if (v !== 'Project') lead.doc.property_project = '' }"
                  />
                </div>
                <SelectField
                  v-if="lead.doc.property_relation === 'Project'"
                  v-model="lead.doc.property_project"
                  :options="projects.data?.map(p => ({ value: p.name, label: p.project_name || p.name })) ?? []"
                  :placeholder="projects.data?.length ? __('Select project') : __('No results found')"
                  :class="{ 'border-red-400 bg-red-50': fieldError === 'property_project' }"
                />
              </FieldWrap>

              <FieldWrap :label="__('Year Built')">
                <input v-model="lead.doc.property_year_built" type="text"
                  inputmode="numeric" pattern="[0-9]*" maxlength="4" class="fi"
                  :class="{ 'border-red-400 bg-red-50': fieldError === 'property_year_built' }"
                  placeholder="e.g. 2022" />
              </FieldWrap>

              <FieldWrap :label="__('Expected Delivery Date')">
                <input v-model="lead.doc.property_delivery_date" type="date" class="fi"
                  :min="todayDate"
                  :class="{ 'border-red-400 bg-red-50': fieldError === 'property_delivery_date' }" />
              </FieldWrap>

              <FieldWrap :label="__('View Preference')">
                <SelectField v-model="lead.doc.property_view"
                  :options="OPT.property_view" placeholder="" />
              </FieldWrap>

              <FieldWrap :label="__('Key Feature')">
                <SelectField v-model="lead.doc.property_features"
                  :options="OPT.property_features" placeholder="" />
              </FieldWrap>

            </PropCard>

            <!-- ── Column 3: Rooms + Financial + Notes ── -->
            <div class="flex flex-col gap-5">

              <PropCard :title="__('Room Details')">
                <div class="grid grid-cols-2 gap-4">
                  <FieldWrap :label="__('Bedrooms')">
                    <SelectField v-model="lead.doc.property_bedrooms"
                      :options="OPT.property_bedrooms" :placeholder="__('Any')" />
                  </FieldWrap>
                  <FieldWrap :label="__('Bathrooms')">
                    <SelectField v-model="lead.doc.property_bathrooms"
                      :options="OPT.property_bathrooms" :placeholder="__('Any')" />
                  </FieldWrap>
                </div>
              </PropCard>

              <PropCard :title="__('Financial Preference')">

                <!-- Min Budget — label shows EGP or SAR dynamically -->
                <FieldWrap :label="`${__('Min Budget')} (${currency})`">
                  <div :class="fieldError === 'property_min_price' ? 'border border-red-400 bg-red-50 rounded-lg p-2' : ''">
                    <Slider v-model="lead.doc.property_min_price"
                      :max="PRICE_MAX" :format="formatPrice" />
                  </div>
                </FieldWrap>

                <!-- Max Budget — label shows EGP or SAR dynamically -->
                <FieldWrap :label="`${__('Max Budget')} (${currency})`">
                  <div :class="fieldError === 'property_max_price' ? 'border border-red-400 bg-red-50 rounded-lg p-2' : ''">
                    <Slider v-model="lead.doc.property_max_price"
                      :max="PRICE_MAX" :format="formatPrice" />
                  </div>
                </FieldWrap>

                <FieldWrap :label="__('Payment Method')">
                  <div class="flex flex-wrap gap-2">
                    <TypeChip v-for="p in OPT.property_payment" :key="p"
                      v-model="lead.doc.property_payment" :value="p" :label="__(p)" />
                  </div>
                </FieldWrap>

                <FieldWrap
                  v-if="lead.doc.property_payment && lead.doc.property_payment !== OPT.property_payment[0]"
                  :label="__('Down Payment (%)')">
                  <input v-model.number="lead.doc.property_down_payment"
                    type="number" min="0" max="100" step="5" class="fi"
                    :class="{ 'border-red-400 bg-red-50': fieldError === 'property_down_payment' }"
                    placeholder="e.g. 20" />
                </FieldWrap>

                <FieldWrap :label="__('Ownership Type')">
                  <div class="flex flex-wrap gap-2">
                    <TypeChip v-for="o in OPT.property_ownership" :key="o"
                      v-model="lead.doc.property_ownership" :value="o" :label="__(o)" />
                  </div>
                </FieldWrap>

              </PropCard>

              <PropCard :title="__('Notes')">
                <textarea v-model="lead.doc.notes" maxlength="1000"
                  class="w-full border border-gray-200 rounded-lg p-3 text-sm text-gray-700 resize-none focus:outline-none focus:border-[#4A90E2] transition-colors"
                  :class="{ 'border-red-400 bg-red-50': fieldError === 'notes' }"
                  rows="4" :placeholder="__('Add any additional notes...')" />
                <p v-if="(lead.doc.notes || '').length >= 900"
                  class="text-xs mt-1"
                  :class="(lead.doc.notes || '').length >= 1000 ? 'text-red-500' : 'text-amber-500'">
                  {{ (lead.doc.notes || '').length }}/1000
                </p>
              </PropCard>

            </div>
          </div>
        </section>

        <!-- ── Footer ── -->
        <div class="flex items-center justify-between pt-4 border-t border-gray-100">
          <p v-if="error" class="text-sm text-red-500 flex items-center gap-1.5">
            <span>⚠</span> {{ __(error) }}
          </p>
          <div v-else />
          <div class="flex gap-3">
            <button @click="show = false"
              class="px-6 py-2 rounded-lg border border-[#4A90E2] text-[#4A90E2] font-semibold text-sm hover:bg-blue-50 transition-colors">
              {{ __('Cancel') }}
            </button>
            <button @click="createNewLead" :disabled="isLeadCreating"
              class="px-6 py-2 rounded-lg bg-[#4A90E2] text-white font-semibold text-sm hover:bg-[#3B7DCC] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
              <span v-if="isLeadCreating" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              {{ isLeadCreating ? __('Saving...') : __('Add Lead') }}
            </button>
          </div>
        </div>

      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { usersStore }    from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { sessionStore }  from '@/stores/session'
import { showQuickEntryModal, quickEntryProps } from '@/composables/modals'
import { capture }       from '@/telemetry'
import { createResource } from 'frappe-ui'
import { useOnboarding } from 'frappe-ui/frappe'
import { useDocument }   from '@/data/document'
import { computed, defineComponent, h, onMounted, ref, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({ defaults: Object })

const { user }    = sessionStore()
const { getUser } = usersStore()
const { statusOptions } = statusesStore()
const { updateOnboardingStep } = useOnboarding('frappecrm')

const show           = defineModel()
const router         = useRouter()
const error          = ref(null)
const fieldError     = ref(null)
const isLeadCreating = ref(false)
const currentYear    = new Date().getFullYear()
const todayDate      = new Date().toISOString().split('T')[0]

const SPACE_MAX = 500

// ─── Currency — driven by country selection, no field dependency ──────────────

const isSaudi = computed(() => lead.doc?.property_country === 'Saudi Arabia')

// Different price ceilings per market
const PRICE_MAX = computed(() => isSaudi.value ? 10_000_000 : 5_000_000)

const currency = computed(() => isSaudi.value ? 'SAR' : 'EGP')

function formatPrice(val) {
  const sym = currency.value
  if (val >= 1_000_000) return (val / 1_000_000).toFixed(1) + 'M ' + sym
  if (val >= 1_000)     return (val / 1_000).toFixed(0)     + 'K ' + sym
  return val + ' ' + sym
}

// ─── Phone normalization (mirrors backend duplicate_lead.py) ──────────────────

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

// ─── Location data: Country → City → Region ───────────────────────────────────

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
  'Cairo':   ['Downtown Cairo','Garden City','Zamalek','Heliopolis','Nasr City','Madinet Nasr','Shoubra','Shubra El Kheima','Mohandessin','Agouza','Dokki'],
  'New Cairo':['New Cairo - 1st Settlement','New Cairo - 3rd Settlement','New Cairo - 5th Settlement','Beit El Watan','Al Rehab City','Madinaty','Mostakbal City'],
  'Nasr City':['Madinet Nasr','Nasr City'],
  'Heliopolis':['Heliopolis','Korba','Al Nozha','Al Merghany'],
  'Maadi':   ['Maadi','Degla','Sarayat','Zohour','New Maadi'],
  '6th of October':['6th of October - Hay 1','6th of October - Hay 2','6th of October - Hay 3'],
  'Sheikh Zayed':['Sheikh Zayed - Hay 1','Sheikh Zayed - Hay 2'],
  'Zamalek': ['Zamalek'],
  'New Administrative Capital':['New Administrative Capital - R1','New Administrative Capital - R2','New Administrative Capital - R3'],
  'Al Shorouk City':['Al Shorouk City'],
  'Al Obour City':['Al Obour City'],
  'Alexandria':['Smouha','Gleem','San Stefano','Sidi Bishr','Miami','Agami','Borg El Arab'],
  'Giza':    ['Giza','Dokki','Agouza','Mohandessin','Faisal','Haram'],
  'North Coast':['Sahel','Marassi','Hacienda Bay','Sidi Abdel Rahman','Marina'],
  'Ain Sokhna':['Ain Sokhna'],
  'El Gouna':['El Gouna'],
  'Hurghada':['Hurghada'],
  'Sharm El Sheikh':['Sharm El Sheikh'],
  'Riyadh':  ['Al Malaz','Al Muruj','Al Olaya','Al Sulaimaniyah','Al Rawdah','Al Narjis','Al Yasmin','Al Qirawan','Hittin','Al Sahafah','Al Nakheel','Al Aqiq','Diplomatic Quarter','King Abdullah District'],
  'Jeddah':  ['Al Hamra','Al Rawdah','Al Zahraa','Al Shati','Al Naim','Al Marwah','Al Salamah','Al Faisaliyah','Al Balad','Al Khalidiyah','Al Aziziyah','Al Safa','Al Rehab','Al Bawadi'],
  'Makkah':  ['Al Aziziyah','Al Zaher','Al Adl','Ajyad','Al Naseem'],
  'Madinah': ['Al Haram','Al Awali','Quba','Al Anbariyah'],
  'Dammam':  ['Al Faisaliyah','Al Shula','Al Badiyah','Al Noor','Al Nur'],
  'Khobar':  ['Al Thuqbah','Al Aqrabiyah','Al Ulaya','Al Corniche'],
  'Dhahran': ['Dhahran'],
  'Abha':    ['Al Manhal','Al Wurood','Abha Al Jadeedah'],
  'Tabuk':   ['Tabuk'],
  'Yanbu':   ['Yanbu'],
  'Najran':  ['Najran'],
  'Hail':    ['Hail'],
  'Al Khobar':['Al Khobar'],
  'Jubail':  ['Jubail Industrial City','Al Jubail'],
}

// ─── Combobox state ───────────────────────────────────────────────────────────

const cityInput    = ref('')
const showCityDrop = ref(false)
const cityHi       = ref(0)

const regionInput    = ref('')
const showRegionDrop = ref(false)
const regionHi       = ref(0)

const filteredCities = computed(() => {
  const country = lead.doc?.property_country || ''
  const base = country ? (COUNTRY_CITIES[country] || []) : Object.values(COUNTRY_CITIES).flat()
  const q = cityInput.value.toLowerCase().trim()
  return q ? base.filter(c => c.toLowerCase().includes(q)) : base
})

const filteredRegions = computed(() => {
  const city = lead.doc?.property_city || ''
  let base = CITY_REGIONS[city] || []
  if (!base.length) {
    const match = Object.keys(CITY_REGIONS).find(k =>
      k.toLowerCase().includes(city.toLowerCase()) || city.toLowerCase().includes(k.toLowerCase())
    )
    base = match ? CITY_REGIONS[match] : []
  }
  if (!base.length) base = Object.values(CITY_REGIONS).flat()
  const unique = [...new Set(base)]
  const q = regionInput.value.toLowerCase().trim()
  return q ? unique.filter(r => r.toLowerCase().includes(q)) : unique
})

function selectCountry(country) {
  lead.doc.property_country = lead.doc.property_country === country ? '' : country
  cityInput.value = ''
  lead.doc.property_city = ''
  regionInput.value = ''
  lead.doc.property_region = ''
  // Reset price sliders to 0 when switching markets
  lead.doc.property_min_price = 0
  lead.doc.property_max_price = 0
}

function onCityInput() {
  lead.doc.property_city = cityInput.value
  cityHi.value = 0
  showCityDrop.value = true
  regionInput.value = ''
  lead.doc.property_region = ''
}

function pickCity(city) {
  if (!city) return
  cityInput.value = city
  lead.doc.property_city = city
  showCityDrop.value = false
  regionInput.value = ''
  lead.doc.property_region = ''
}

function clearCity() {
  cityInput.value = ''
  lead.doc.property_city = ''
  regionInput.value = ''
  lead.doc.property_region = ''
}

function onCityBlur() {
  setTimeout(() => {
    showCityDrop.value = false
    lead.doc.property_city = cityInput.value
  }, 150)
}

function onRegionInput() {
  lead.doc.property_region = regionInput.value
  regionHi.value = 0
  showRegionDrop.value = true
}

function pickRegion(region) {
  if (!region) return
  regionInput.value = region
  lead.doc.property_region = region
  showRegionDrop.value = false
}

function clearRegion() {
  regionInput.value = ''
  lead.doc.property_region = ''
}

function onRegionBlur() {
  setTimeout(() => {
    showRegionDrop.value = false
    lead.doc.property_region = regionInput.value
  }, 150)
}

// ─── Doctype options (no city/region — those are now free-text) ───────────────

const DOCTYPE_JSON = {
  fields: [
    { fieldname: 'lead_type',           fieldtype: 'Select', options: '\nOut Source\nCompany' },
    { fieldname: 'property_type',       fieldtype: 'Select', options: '\nResidential\nCommercial\nAdministrative\nLand' },
    { fieldname: 'property_subtype',    fieldtype: 'Select', options: '\nApartment\nDuplex\nPenthouse\nStudio\nVilla\nTwin House\nTownhouse\nChalet\nCabin\nOffice\nShop\nClinic\nWarehouse\nShowroom\nAdministrative Office\nPlot - Residential\nPlot - Commercial\nPlot - Industrial' },
    { fieldname: 'property_floor',      fieldtype: 'Select', options: '\nGround Floor\n1st Floor\n2nd Floor\n3rd Floor\n4th Floor\n5th Floor\n6th Floor\n7th Floor\n8th Floor\n9th Floor\n10th Floor\nHigh Floor (10+)\nRooftop / Penthouse\nBasement\nNo Preference' },
    { fieldname: 'property_condition',  fieldtype: 'Select', options: '\nNew / Off-Plan\nUnder Construction\nReady to Move\nRenovated\nNeed Repair\nOld Building' },
    { fieldname: 'property_decoration', fieldtype: 'Select', options: '\nFurnished\nSemi-Furnished\nUnfurnished\nCore & Shell\nSemi-Finished\nFully Finished\nSuper Lux\nUltra Lux' },
    { fieldname: 'property_relation',   fieldtype: 'Select', options: '\nStand Alone\nProject\nCompound' },
    { fieldname: 'property_bedrooms',   fieldtype: 'Select', options: '\nStudio\n1\n2\n3\n4\n5\n6+' },
    { fieldname: 'property_bathrooms',  fieldtype: 'Select', options: '\n1\n2\n3\n4\n5+' },
    { fieldname: 'property_view',       fieldtype: 'Select', options: '\nStreet View\nGarden View\nPool View\nLake View\nSea View\nCity View\nNo Preference' },
    { fieldname: 'property_finishing',  fieldtype: 'Select', options: '\nCore & Shell\nSemi-Finished\nFully Finished\nSuper Lux\nUltra Lux' },
    { fieldname: 'property_features',   fieldtype: 'Select', options: '\nPrivate Garden\nPrivate Pool\nShared Pool\nGym\nGarage\nElevator\nSecurity / Gated\nSmart Home\nSea Access\nLake / Lagoon\nGolf Course View\nPet Friendly\nStorage Room\nMaid Room\nDriver Room' },
    { fieldname: 'property_payment',    fieldtype: 'Select', options: '\nCash\nInstallment\nMortgage\nBank Loan' },
    { fieldname: 'property_ownership',  fieldtype: 'Select', options: '\nBuy\nRent\nRent-to-Own' },
  ],
}

function parseSelectOptions(json) {
  const opts = {}
  for (const field of json.fields) {
    if (field.fieldtype === 'Select' && field.options) {
      opts[field.fieldname] = field.options.split('\n').filter(s => s.trim())
    }
  }
  return opts
}

const OPT = parseSelectOptions(DOCTYPE_JSON)

const SUBTYPES_BY_TYPE = {
  Residential:    ['Apartment','Duplex','Penthouse','Studio','Villa','Twin House','Townhouse','Chalet','Cabin'],
  Commercial:     ['Shop','Showroom','Warehouse'],
  Administrative: ['Office','Administrative Office','Clinic'],
  Land:           ['Plot - Residential','Plot - Commercial','Plot - Industrial'],
}

const currentSubtypes = computed(() =>
  lead.doc?.property_type ? (SUBTYPES_BY_TYPE[lead.doc.property_type] ?? []) : []
)

const currentFinishingOptions = computed(() => {
  const all = OPT.property_finishing || []
  return lead.doc?.property_decoration === 'Core & Shell'
    ? all.filter(o => o !== 'Fully Finished')
    : all
})

watch(() => lead.doc?.property_decoration, (val) => {
  if (val === 'Core & Shell' && lead.doc?.property_finishing === 'Fully Finished') {
    lead.doc.property_finishing = ''
  }
})

// ─── Inline sub-components ────────────────────────────────────────────────────

const SectionHeader = defineComponent({
  props: { title: String },
  setup(p) {
    return () => h('div', { class: 'flex items-center gap-3 mb-1' }, [
      h('span', { class: 'text-xs font-bold uppercase tracking-widest text-[#4A90E2]' }, p.title),
      h('div',  { class: 'flex-1 h-px bg-gradient-to-r from-[#4A90E2]/30 to-transparent' }),
    ])
  },
})

const PropCard = defineComponent({
  props: { title: String },
  setup(p, { slots }) {
    return () => h('div', {
      class: 'border border-gray-100 rounded-xl p-5 flex flex-col gap-4 bg-white shadow-sm',
    }, [
      h('div', { class: 'flex flex-col gap-1' }, [
        h('p',   { class: 'font-semibold text-sm text-gray-600' }, p.title),
        h('div', { class: 'w-12 h-0.5 bg-[#4A90E2]/40 rounded' }),
      ]),
      slots.default?.(),
    ])
  },
})

const FieldWrap = defineComponent({
  props: { label: String, required: Boolean },
  setup(p, { slots }) {
    return () => h('div', { class: 'flex flex-col gap-1' }, [
      h('label', { class: 'text-xs font-semibold text-gray-500 flex items-center gap-1' }, [
        p.label,
        p.required ? h('span', { class: 'text-red-400' }, '*') : null,
      ]),
      slots.default?.(),
    ])
  },
})

const RadioBtn = defineComponent({
  props: { modelValue: String, value: String, label: String, name: String },
  emits: ['update:modelValue'],
  setup(p, { emit }) {
    return () => h('label', { class: 'flex items-center gap-1.5 cursor-pointer group' }, [
      h('input', {
        type: 'radio', name: p.name, value: p.value,
        checked: p.modelValue === p.value,
        onChange: () => emit('update:modelValue', p.value),
        class: 'w-4 h-4 accent-[#4A90E2]',
      }),
      h('span', { class: 'text-sm text-gray-700 group-hover:text-[#4A90E2] transition-colors' }, p.label),
    ])
  },
})

const TypeChip = defineComponent({
  props: { modelValue: String, value: String, label: String },
  emits: ['update:modelValue'],
  setup(p, { emit }) {
    return () => h('button', {
      type: 'button',
      onClick: () => emit('update:modelValue', p.modelValue === p.value ? '' : p.value),
      class: [
        'px-3 py-1.5 rounded-full text-xs font-semibold border transition-all duration-150',
        p.modelValue === p.value
          ? 'bg-[#4A90E2] text-white border-[#4A90E2] shadow-sm'
          : 'bg-white text-gray-500 border-gray-200 hover:border-[#4A90E2] hover:text-[#4A90E2]',
      ].join(' '),
    }, p.label)
  },
})

const SelectField = defineComponent({
  props: {
    modelValue:  String,
    options:     { type: Array, default: () => [] },
    placeholder: { type: String, default: '' },
    disabled:    { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  setup(p, { emit }) {
    const normalizedOptions = computed(() =>
      (p.options ?? []).map(o =>
        typeof o === 'string' ? { value: o, label: o } : { value: o.value, label: o.label ?? o.value }
      )
    )
    return () => {
      const hasOptions = normalizedOptions.value.length > 0
      const showPlaceholder = !!p.placeholder || !hasOptions
      return h('select', {
        value: p.modelValue || '',
        disabled: p.disabled,
        onChange: e => emit('update:modelValue', e.target.value),
        class: ['select-fi fi', p.disabled ? 'bg-gray-50 text-gray-300 cursor-not-allowed' : '', !p.modelValue ? 'text-gray-400' : 'text-gray-700'].join(' '),
      }, [
        ...(showPlaceholder ? [h('option', { value: '', disabled: true, selected: !p.modelValue, hidden: !!p.modelValue }, p.placeholder || __('No results found'))] : []),
        ...normalizedOptions.value.map(o => h('option', { value: o.value }, o.label)),
      ])
    }
  },
})

const Slider = defineComponent({
  props: {
    modelValue: { type: Number, default: 0 },
    max:        { type: Number, default: 100 },
    format:     { type: Function, default: v => v },
  },
  emits: ['update:modelValue'],
  setup(p, { emit }) {
    const trackRef = ref(null)
    const pct = computed(() => Math.min(100, Math.max(0, ((p.modelValue ?? 0) / p.max) * 100)))

    function applyPos(clientX) {
      const el = trackRef.value
      if (!el) return
      const rect = el.getBoundingClientRect()
      const pc = Math.min(100, Math.max(0, (clientX - rect.left) / rect.width * 100))
      emit('update:modelValue', Math.round((pc / 100) * p.max))
    }

    function startDrag(e) {
      e.preventDefault()
      applyPos(e.clientX)
      const move = e => applyPos(e.clientX)
      const up   = () => { document.removeEventListener('mousemove', move); document.removeEventListener('mouseup', up) }
      document.addEventListener('mousemove', move)
      document.addEventListener('mouseup', up)
    }

    return () => {
      const pc = pct.value
      return h('div', { class: 'flex flex-col gap-2 pt-5' }, [
        h('div', { class: 'relative' }, [
          h('div', { ref: trackRef, onMousedown: startDrag, class: 'w-full h-2 bg-gray-200 rounded-full cursor-pointer select-none relative' }, [
            h('div', { class: 'absolute h-2 bg-[#4A90E2] rounded-full pointer-events-none', style: { width: pc + '%' } }),
            h('div', { class: 'absolute w-4 h-4 bg-white border-2 border-[#4A90E2] rounded-full shadow -translate-y-1 -translate-x-1/2 pointer-events-none', style: { left: pc + '%', top: '0' } }),
          ]),
          h('div', { class: 'absolute -top-6 -translate-x-1/2 bg-[#4A90E2] text-white text-[10px] rounded px-1.5 py-0.5 pointer-events-none whitespace-nowrap', style: { left: pc + '%' } }, p.format(p.modelValue ?? 0)),
        ]),
        h('div', { class: 'flex justify-between text-[10px] text-gray-400' }, [
          h('span', p.format(0)),
          h('span', p.format(p.max)),
        ]),
      ])
    }
  },
})

// ─── Remote resources ─────────────────────────────────────────────────────────

const salutations  = createResource({ url: 'frappe.client.get_list', params: { doctype: 'Salutation',         fields: ['name'], limit_page_length: 50,  order_by: 'name asc' }, auto: true })
const leadSources  = createResource({ url: 'frappe.client.get_list', params: { doctype: 'CRM Lead Source',    fields: ['name'], limit_page_length: 100, order_by: 'name asc' }, auto: true })
const territories  = createResource({ url: 'frappe.client.get_list', params: { doctype: 'CRM Territory',     fields: ['name'], limit_page_length: 200, order_by: 'name asc' }, auto: true })
const industries   = createResource({ url: 'frappe.client.get_list', params: { doctype: 'CRM Industry',      fields: ['name'], limit_page_length: 200, order_by: 'name asc' }, auto: true })
const projects     = createResource({ url: 'frappe.client.get_list', params: { doctype: 'Real Estate Project', fields: ['name','project_name'], limit_page_length: 999, order_by: 'project_name asc' }, auto: true })
const projectUnits = createResource({ url: 'frappe.client.get_list', params: { doctype: 'Project Unit',      fields: ['name','unit_name','project'], limit_page_length: 999, order_by: 'unit_name asc' }, auto: true })
const units        = createResource({ url: 'frappe.client.get_list', params: { doctype: 'Unit',              fields: ['name','unit_name'], limit_page_length: 999, order_by: 'unit_name asc' }, auto: true })

function onLeadProjectChange() { lead.doc.project_unit = '' }

const filteredProjectUnits = computed(() => {
  if (!lead.doc?.project || !projectUnits.data) return []
  return projectUnits.data.filter(u => u.project === lead.doc.project)
})

// ─── Document ─────────────────────────────────────────────────────────────────

const { document: lead, triggerOnBeforeCreate } = useDocument('CRM Lead')

const leadStatuses = computed(() => {
  const statuses = statusOptions('lead')
  if (!lead.doc.status) lead.doc.status = statuses?.[0]?.value
  return statuses
})

// ─── Helpers ──────────────────────────────────────────────────────────────────

const createLead     = createResource({ url: 'frappe.client.insert' })
const createLeadNote = createResource({ url: 'frappe.client.insert' })

function stripHtml(html) {
  return String(html || '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/?(strong|b|em|i|span|div|p)[^>]*>/gi, '')
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/\s+/g, ' ')
    .trim()
}

function isBlank(value) { return String(value ?? '').trim() === '' }

function validateMax(field, label, max) {
  if (String(lead.doc[field] ?? '').length > max) {
    fieldError.value = field
    error.value = __(`${label} cannot exceed ${max} characters`)
    return error.value
  }
  return null
}

function validateNumberRange(field, label, min, max) {
  const value = lead.doc[field]
  if (value == null || value === '') return null
  const num = Number(value)
  if (Number.isNaN(num)) {
    fieldError.value = field
    error.value = __(`${label} must be a valid number`)
    return error.value
  }
  if (num < min || num > max) {
    fieldError.value = field
    error.value = __(`${label} must be between ${min} and ${max}`)
    return error.value
  }
  return null
}

// ─── Create lead ──────────────────────────────────────────────────────────────

async function createNewLead() {
  await triggerOnBeforeCreate?.()

  createLead.submit(
    { doc: { doctype: 'CRM Lead', ...lead.doc, notes: undefined } },
    {
      validate() {
        error.value    = null
        fieldError.value = null

        // ── Required fields ───────────────────────────────────────────────────
        if (isBlank(lead.doc.first_name)) {
          fieldError.value = 'first_name'
          error.value = __('First Name is mandatory')
          return error.value
        }

        const invalidChars = [';','<','>','{','}','[',']']
        if (invalidChars.some(ch => String(lead.doc.first_name || '').includes(ch))) {
          fieldError.value = 'first_name'
          error.value = __('First Name contains invalid characters')
          return error.value
        }

        if (!lead.doc.gender) {
          fieldError.value = 'gender'
          error.value = __('Gender is mandatory')
          return error.value
        }

        if (isBlank(lead.doc.mobile_no)) {
          fieldError.value = 'mobile_no'
          error.value = __('Mobile No is mandatory')
          return error.value
        }

        if (!lead.doc.status) {
          error.value = __('Status is required')
          return error.value
        }

        if (isBlank(lead.doc.lead_owner)) {
          fieldError.value = 'lead_owner'
          error.value = __('Lead Owner is required')
          return error.value
        }

        // ── Max-length ────────────────────────────────────────────────────────
        if (validateMax('first_name',       'First Name',        50))  return error.value
        if (validateMax('last_name',        'Last Name',         140)) return error.value
        if (validateMax('email',            'Email',             140)) return error.value
        if (validateMax('mobile_no',        'Mobile No',         20))  return error.value
        if (validateMax('phone',            'Other Phone',       20))  return error.value
        if (validateMax('property_city',    'City',              140)) return error.value
        if (validateMax('property_region',  'Region / District', 140)) return error.value
        if (validateMax('property_project', 'Project Name',      140)) return error.value
        if (validateMax('notes',            'Notes',             1000)) return error.value

        // ── Mobile validation — Egypt OR Saudi ────────────────────────────────
        if (!isValidPhone(lead.doc.mobile_no)) {
          fieldError.value = 'mobile_no'
          error.value = __('Enter a valid Egyptian (01xxxxxxxxx) or Saudi (05xxxxxxxx) mobile number')
          return error.value
        }

        // ── Other phone (optional) — Egypt OR Saudi ───────────────────────────
        if (!isBlank(lead.doc.phone) && !isValidPhone(lead.doc.phone)) {
          fieldError.value = 'phone'
          error.value = __('Other Phone must be a valid Egyptian or Saudi number')
          return error.value
        }

        // ── Email ─────────────────────────────────────────────────────────────
        if (!isBlank(lead.doc.email)) {
          if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(lead.doc.email).trim())) {
            fieldError.value = 'email'
            error.value = __('Invalid Email address')
            return error.value
          }
        }

        // ── Property relation → project required ──────────────────────────────
        if (lead.doc.property_relation === 'Project') {
          if (isBlank(lead.doc.property_project)) {
            fieldError.value = 'property_project'
            error.value = __('Project Name is mandatory when Property Relation is Project')
            return error.value
          }
          const validNames = (projects.data || []).map(p => p.name)
          if (!validNames.includes(lead.doc.property_project)) {
            fieldError.value = 'property_project'
            error.value = __('Please select a valid project from the list')
            return error.value
          }
        }

        // ── Year built ────────────────────────────────────────────────────────
        if (!isBlank(lead.doc.property_year_built)) {
          const yr = String(lead.doc.property_year_built).trim()
          if (!/^\d{4}$/.test(yr)) {
            fieldError.value = 'property_year_built'
            error.value = __('Year Built must be a 4-digit year')
            return error.value
          }
          const num = Number(yr)
          if (num < 1900 || num > currentYear) {
            fieldError.value = 'property_year_built'
            error.value = __(`Year Built must be between 1900 and ${currentYear}`)
            return error.value
          }
          lead.doc.property_year_built = num
        }

        // ── Numeric ranges ────────────────────────────────────────────────────
        if (validateNumberRange('property_down_payment', 'Down Payment', 0, 100)) return error.value

        const priceMax = PRICE_MAX.value
        if (lead.doc.property_space != null && lead.doc.property_space !== '') {
          const v = Number(lead.doc.property_space)
          if (Number.isNaN(v) || v < 0 || v > SPACE_MAX) {
            fieldError.value = 'property_space'
            error.value = __(`Space (sqm) must be between 0 and ${SPACE_MAX}`)
            return error.value
          }
        }
        if (lead.doc.property_min_price != null && lead.doc.property_min_price !== '') {
          const v = Number(lead.doc.property_min_price)
          if (Number.isNaN(v) || v < 0 || v > priceMax) {
            fieldError.value = 'property_min_price'
            error.value = __(`Min Budget must be between 0 and ${priceMax.toLocaleString()} ${currency.value}`)
            return error.value
          }
        }
        if (lead.doc.property_max_price != null && lead.doc.property_max_price !== '') {
          const v = Number(lead.doc.property_max_price)
          if (Number.isNaN(v) || v < 0 || v > priceMax) {
            fieldError.value = 'property_max_price'
            error.value = __(`Max Budget must be between 0 and ${priceMax.toLocaleString()} ${currency.value}`)
            return error.value
          }
        }
        if (
          lead.doc.property_min_price != null && lead.doc.property_max_price != null &&
          lead.doc.property_min_price !== ''   && lead.doc.property_max_price !== '' &&
          Number(lead.doc.property_min_price) > Number(lead.doc.property_max_price)
        ) {
          fieldError.value = 'property_min_price'
          error.value = __('Min Budget cannot exceed Max Budget')
          return error.value
        }

        // ── Delivery date ─────────────────────────────────────────────────────
        if (lead.doc.property_delivery_date) {
          const d = new Date(lead.doc.property_delivery_date)
          if (Number.isNaN(d.getTime())) {
            fieldError.value = 'property_delivery_date'
            error.value = __('Expected Delivery Date is invalid')
            return error.value
          }
          const today = new Date(); today.setHours(0,0,0,0); d.setHours(0,0,0,0)
          if (d < today) {
            fieldError.value = 'property_delivery_date'
            error.value = __('Expected delivery date must be today or a future date')
            return error.value
          }
        }

        // ── Decoration / finishing conflict ───────────────────────────────────
        if (lead.doc.property_decoration === 'Core & Shell' && lead.doc.property_finishing === 'Fully Finished') {
          fieldError.value = 'property_finishing'
          error.value = __('Fully Finished is not allowed when Decoration Status is Core & Shell')
          return error.value
        }

        isLeadCreating.value = true
      },

      async onSuccess(data) {
        capture('lead_created')
        const noteText = String(lead.doc.notes || '').trim()
        if (noteText) {
          try {
            await createLeadNote.submit({
              doc: {
                doctype: 'FCRM Note', title: __('Lead Note'), content: noteText,
                reference_doctype: 'CRM Lead', reference_docname: data.name,
              },
            })
          } catch (e) { console.error('Failed to create lead note', e) }
        }
        isLeadCreating.value = false
        show.value = false
        router.push({ name: 'Lead', params: { leadId: data.name } })
        updateOnboardingStep('create_first_lead', true, false, () => {
          localStorage.setItem('firstLead' + user, data.name)
        })
      },

      onError(err) {
        isLeadCreating.value = false
        const rawMessage = err?.messages?.join('\n') || err?.messages?.[0] || err?.message || err?.exc_type || __('Something went wrong')
        let clean = stripHtml(rawMessage)
          .replace(/^MandatoryError:\s*/i, '')
          .replace(/^ValidationError:\s*/i, '')
          .replace(/^Error:\s*/i, '')
          .trim()
        error.value = clean
      },
    },
  )
}

// ─── Lifecycle ────────────────────────────────────────────────────────────────

onMounted(() => {
  lead.doc = {
    property_min_price: 0,
    property_max_price: 0,
    property_space:     0,
  }
  Object.assign(lead.doc, props.defaults)
  if (!lead.doc?.lead_owner) lead.doc.lead_owner = getUser().name
  if (!lead.doc?.status && leadStatuses.value[0]?.value) {
    lead.doc.status = leadStatuses.value[0].value
  }
})
</script>

<style scoped>
.fi {
  @apply w-full h-10 bg-white border border-gray-200 rounded-lg px-3 text-sm text-gray-700
         focus:outline-none focus:border-[#4A90E2] focus:ring-2 focus:ring-[#4A90E2]/10
         transition-colors placeholder-gray-300;
}
.select-fi {
  @apply appearance-none cursor-pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%239ca3af' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 2rem;
}
</style>