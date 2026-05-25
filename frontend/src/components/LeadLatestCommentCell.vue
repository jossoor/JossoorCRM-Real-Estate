<template>
  <div class="latest-comment-cell" @click.stop @mousedown.stop>
    <div class="latest-comment-actions">
      <button type="button" class="latest-comment-action" @click.stop="openViewer">
        {{ __("View") }}
      </button>
      <LeadCommentsQuick
        :leadName="leadName"
        buttonOnly
        :triggerLabel="__('Add')"
        @saved="handleSaved"
      />
    </div>

    <button
      type="button"
      class="latest-comment-content"
      @click.stop="openViewer"
    >
      <div v-if="hasFeedback" class="latest-comment-summary">
        <span class="latest-comment-type">
          {{ latestType }}
        </span>
        <span v-if="latestTitle" class="latest-comment-title truncate text-ink-gray-8">
          {{ latestTitle }}:
        </span>
        <span class="latest-comment-inline-description text-ink-gray-6">
          {{ latestDescription }}
        </span>
      </div>
      <div v-else class="latest-comment-empty text-ink-gray-4">
        {{ __("No feedback yet") }}
      </div>
    </button>

    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-150 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div v-if="showViewer" class="fixed inset-0 z-[100] flex items-center justify-center p-4" role="dialog">
          <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeViewer"></div>

          <div class="relative flex max-h-[90vh] w-full max-w-3xl flex-col rounded-2xl bg-white shadow-xl">
            <button
              type="button"
              class="absolute -right-3 -top-3 z-[110] flex h-8 w-8 items-center justify-center rounded-full bg-blue-500 text-xl font-bold text-white shadow-md transition-colors hover:bg-blue-600"
              @click="closeViewer"
            >
              x
            </button>

            <div class="border-b border-outline-gray-2 px-6 py-5">
              <h2 class="text-xl font-semibold text-ink-gray-9">{{ __("Feedback") }}</h2>
            </div>

            <div class="min-h-0 flex-1 overflow-y-auto px-6 py-5">
              <div v-if="viewerLoading" class="py-8 text-center text-sm text-ink-gray-5">
                {{ __("Loading...") }}
              </div>
              <div v-else-if="viewerError" class="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                {{ viewerError }}
              </div>
              <div v-else-if="!comments.length" class="py-8 text-center text-sm text-ink-gray-5">
                {{ __("No feedback yet") }}
              </div>
              <div v-else class="space-y-4">
                <article
                  v-for="comment in comments"
                  :key="comment.name"
                  class="rounded-lg border border-outline-gray-2 bg-surface-white px-4 py-3"
                >
                  <div class="mb-2 flex min-w-0 items-start justify-between gap-3">
                    <div class="min-w-0">
                      <div class="flex min-w-0 items-center gap-2">
                        <span class="latest-comment-type">
                          {{ subjectParts(comment.subject).type }}
                        </span>
                        <span class="truncate text-sm font-semibold text-ink-gray-9">
                          {{ subjectParts(comment.subject).title || __("Feedback") }}
                        </span>
                      </div>
                      <div class="mt-1 text-xs text-ink-gray-5">
                        {{ comment.comment_by || comment.owner || "" }}
                      </div>
                    </div>
                    <div class="shrink-0 text-xs text-ink-gray-4">
                      {{ formatDate(comment.creation) }}
                    </div>
                  </div>
                  <div class="whitespace-pre-wrap text-sm leading-6 text-ink-gray-7">
                    {{ stripHtml(comment.content) }}
                  </div>
                </article>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue"
import { call } from "frappe-ui"
import LeadCommentsQuick from "@/components/LeadCommentsQuick.vue"
import { FEEDBACK_TYPES } from "@/constants/feedbackTypes"

const props = defineProps({
  leadName: {
    type: String,
    required: true,
  },
  fallbackText: {
    type: [String, Object],
    default: "",
  },
})

const latest = ref(null)
const comments = ref([])
const showViewer = ref(false)
const viewerLoading = ref(false)
const viewerError = ref("")

function stripHtml(value) {
  if (!value) return ""
  return String(value)
    .replace(/<[^>]*>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/\s+/g, " ")
    .trim()
}

function textFromFallback(value) {
  if (!value) return ""
  if (typeof value === "string") return value
  return value.label || value.value || value.content || ""
}

const feedbackTypeMap = new Map(
  FEEDBACK_TYPES.flatMap((option) => [
    [String(option.value || "").toLowerCase(), option.label || option.value || ""],
    [String(option.label || "").toLowerCase(), option.label || option.value || ""],
  ])
)

function normalizeFeedbackType(value) {
  const raw = String(value || "").trim()
  if (!raw) return __("Activity")
  return feedbackTypeMap.get(raw.toLowerCase()) || raw
}

function parseSubject(subject) {
  const raw = String(subject || "").trim()
  if (!raw) return { type: __("Activity"), title: "" }

  const parts = raw.split(/:{3,}/)
  if (parts.length > 1) {
    return {
      type: normalizeFeedbackType(parts[0]),
      title: parts.slice(1).join(":::").trim(),
    }
  }

  return {
    type: normalizeFeedbackType(raw),
    title: "",
  }
}

function subjectParts(subject) {
  return parseSubject(subject)
}

function formatDate(value) {
  if (!value) return ""
  const parsed = new Date(String(value).replace(" ", "T"))
  if (Number.isNaN(parsed.getTime())) return value
  return parsed.toLocaleString()
}

const fallbackDescription = computed(() => stripHtml(textFromFallback(props.fallbackText)))
const parsedSubject = computed(() => parseSubject(latest.value?.subject))
const latestType = computed(() => parsedSubject.value.type || __("Activity"))
const latestTitle = computed(() => parsedSubject.value.title)
const latestDescription = computed(() => {
  return stripHtml(latest.value?.content) || fallbackDescription.value
})
const hasFeedback = computed(() => Boolean(latest.value || fallbackDescription.value))

async function fetchComments(limit = 50) {
  if (!props.leadName) return []

  const response = await call("frappe.client.get_list", {
    doctype: "Comment",
    fields: ["name", "subject", "content", "creation", "owner", "comment_by"],
    filters: [
      ["Comment", "reference_doctype", "=", "CRM Lead"],
      ["Comment", "reference_name", "=", props.leadName],
      ["Comment", "comment_type", "=", "Comment"],
    ],
    order_by: "creation desc",
    limit_page_length: limit,
  })

  return Array.isArray(response?.message)
    ? response.message
    : Array.isArray(response)
      ? response
      : []
}

async function loadLatest() {
  try {
    const rows = await fetchComments(1)
    latest.value = rows[0] || null
  } catch (error) {
    latest.value = null
  }
}

async function loadViewerComments() {
  viewerLoading.value = true
  viewerError.value = ""
  try {
    comments.value = await fetchComments(50)
  } catch (error) {
    viewerError.value = error?.message || __("Failed to load feedback")
  } finally {
    viewerLoading.value = false
  }
}

async function openViewer() {
  showViewer.value = true
  await loadViewerComments()
}

function closeViewer() {
  showViewer.value = false
}

async function handleSaved() {
  await loadLatest()
  if (showViewer.value) await loadViewerComments()
}

onMounted(loadLatest)
watch(() => props.leadName, () => {
  loadLatest()
  if (showViewer.value) loadViewerComments()
})
</script>

<style scoped>
.latest-comment-cell {
  display: grid;
  grid-template-columns: max-content minmax(0, 1fr);
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  min-width: 0;
}

.latest-comment-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: max-content;
}

.latest-comment-action {
  height: 1.75rem;
  border-radius: 0.375rem;
  padding: 0 0.625rem;
  border: 1px solid var(--surface-gray-3, #d1d5db);
  background: white;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink-gray-7, #374151);
}

.latest-comment-content {
  min-width: 0;
  text-align: left;
}

.latest-comment-summary {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  min-width: 0;
  width: 100%;
}

.latest-comment-title {
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1.25rem;
}

.latest-comment-inline-description {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.8125rem;
  line-height: 1.25rem;
}

.latest-comment-empty {
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.latest-comment-type {
  flex-shrink: 0;
  border-radius: 0.25rem;
  border: 1px solid var(--outline-gray-2, #e5e7eb);
  background: var(--surface-gray-1, #f9fafb);
  padding: 0.125rem 0.375rem;
  font-size: 0.6875rem;
  font-weight: 700;
  line-height: 1.125rem;
  text-transform: uppercase;
  color: var(--ink-gray-7, #374151);
}

.latest-comment-description {
  font-size: 0.8125rem;
  line-height: 1.25rem;
  display: -webkit-box;
  overflow: hidden;
  overflow-wrap: anywhere;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
</style>
