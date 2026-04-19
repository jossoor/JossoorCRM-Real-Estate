<template>
  <div class="space-y-6">
    <!-- Reservation -->
    <div
      v-if="hasReservation"
      class="rounded-xl border border-outline-gray-modals bg-surface-white p-5"
    >
      <div class="mb-4 text-lg font-semibold text-ink-gray-9">Reservation</div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-x-8 gap-y-3 text-sm">
        <FieldRow label="Reservation" :value="doc.reservation" />
        <FieldRow label="Reservation Fee" :value="doc.reservation_fee" />
        <FieldRow label="Reservation Date" :value="doc.reservation_date" />
        <FieldRow label="Project" :value="doc.reservation_project" />
        <FieldRow label="Unit" :value="doc.reservation_unit" />
        <FieldRow label="Payment Plan" :value="doc.payment_plan" />
        <FieldRow label="Total Cost" :value="doc.total_cost" />
        <FieldRow label="Per Installment" :value="doc.per_installment" />
        <FieldRow label="Installments" :value="doc.installments" />
        <FieldRow label="Years" :value="doc.years" />
        <FieldRow label="Frequency" :value="doc.frequency" />
      </div>
    </div>

    <!-- Property Preferences -->
    <div
      v-if="hasProperty"
      class="rounded-xl border border-outline-gray-modals bg-surface-white p-5"
    >
      <div class="mb-4 text-lg font-semibold text-ink-gray-9">Property Preferences</div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-x-8 gap-y-3 text-sm">
        <FieldRow label="City" :value="doc.property_city" />
        <FieldRow label="Region" :value="doc.property_region" />
        <FieldRow label="Type" :value="doc.property_type" />
        <FieldRow label="Subtype" :value="doc.property_subtype" />
        <FieldRow label="Space" :value="doc.property_space" />
        <FieldRow label="Floor" :value="doc.property_floor" />
        <FieldRow label="Condition" :value="doc.property_condition" />
        <FieldRow label="Decoration" :value="doc.property_decoration" />
        <FieldRow label="Relation" :value="doc.property_relation" />
        <FieldRow label="Project" :value="doc.property_project" />
        <FieldRow label="Year Built" :value="doc.property_year_built" />
        <FieldRow label="Delivery Date" :value="doc.property_delivery_date" />
        <FieldRow label="Bedrooms" :value="doc.property_bedrooms" />
        <FieldRow label="Bathrooms" :value="doc.property_bathrooms" />
        <FieldRow label="View" :value="doc.property_view" />
        <FieldRow label="Finishing" :value="doc.property_finishing" />
        <FieldRow label="Features" :value="doc.property_features" />
        <FieldRow label="Min Price" :value="doc.property_min_price" />
        <FieldRow label="Max Price" :value="doc.property_max_price" />
        <FieldRow label="Payment" :value="doc.property_payment" />
        <FieldRow label="Down Payment %" :value="doc.property_down_payment" />
        <FieldRow label="Ownership" :value="doc.property_ownership" />
      </div>
    </div>

    <!-- Payment Plan Snapshot -->
    <div
      v-if="hasPlan"
      class="rounded-xl border border-outline-gray-modals bg-surface-white p-5"
    >
      <div class="mb-4 text-lg font-semibold text-ink-gray-9">Payment Plan Snapshot</div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-x-8 gap-y-3 text-sm">
        <FieldRow label="Plan Name" :value="doc.plan_name" />
        <FieldRow label="Notes" :value="doc.plan_notes" />
        <FieldRow label="Area" :value="doc.plan_area" />
        <FieldRow label="Price / m²" :value="doc.plan_price_per_m2" />
        <FieldRow label="Total Price" :value="doc.plan_total_price" />
        <FieldRow label="Down Payment %" :value="doc.plan_downpayment_percent" />
        <FieldRow label="Total DP" :value="doc.plan_total_downpayment_value" />
        <FieldRow label="Start Date" :value="doc.plan_start_date" />
        <FieldRow label="Installment Type" :value="doc.plan_installment_type" />
      </div>
    </div>

    <div
      v-if="!hasReservation && !hasProperty && !hasPlan"
      class="flex h-40 items-center justify-center text-base text-ink-gray-5"
    >
      No reservation data
    </div>
  </div>
</template>

<script setup>
import { computed, defineComponent, h } from 'vue'

const props = defineProps({
  doc: {
    type: Object,
    default: () => ({}),
  },
})

const hasReservation = computed(() =>
  !!(
    props.doc.reservation ||
    props.doc.reservation_fee ||
    props.doc.reservation_date ||
    props.doc.reservation_project ||
    props.doc.reservation_unit ||
    props.doc.payment_plan ||
    props.doc.total_cost ||
    props.doc.per_installment ||
    props.doc.installments ||
    props.doc.years ||
    props.doc.frequency
  ),
)

const hasProperty = computed(() =>
  !!(
    props.doc.property_city ||
    props.doc.property_region ||
    props.doc.property_type ||
    props.doc.property_subtype ||
    props.doc.property_space ||
    props.doc.property_floor ||
    props.doc.property_condition ||
    props.doc.property_decoration ||
    props.doc.property_relation ||
    props.doc.property_project ||
    props.doc.property_year_built ||
    props.doc.property_delivery_date ||
    props.doc.property_bedrooms ||
    props.doc.property_bathrooms ||
    props.doc.property_view ||
    props.doc.property_finishing ||
    props.doc.property_features ||
    props.doc.property_min_price ||
    props.doc.property_max_price ||
    props.doc.property_payment ||
    props.doc.property_down_payment ||
    props.doc.property_ownership
  ),
)

const hasPlan = computed(() =>
  !!(
    props.doc.plan_name ||
    props.doc.plan_notes ||
    props.doc.plan_area ||
    props.doc.plan_price_per_m2 ||
    props.doc.plan_total_price ||
    props.doc.plan_downpayment_percent ||
    props.doc.plan_total_downpayment_value ||
    props.doc.plan_start_date ||
    props.doc.plan_installment_type
  ),
)

const FieldRow = defineComponent({
  name: 'FieldRow',
  props: {
    label: String,
    value: [String, Number, Boolean],
  },
  setup(props) {
    return () =>
      props.value || props.value === 0
        ? h('div', { class: 'flex flex-col border-b border-outline-gray-modals pb-2' }, [
            h('div', { class: 'text-xs font-medium uppercase tracking-wide text-ink-gray-5' }, props.label),
            h('div', { class: 'mt-1 text-sm text-ink-gray-9 break-words' }, String(props.value)),
          ])
        : null
  },
})
</script>