<template>
  <div class="flex flex-col h-full overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs routeName="Dashboard" />
      </template>
      <template #right-header>
        <Button v-if="!editing" :label="__('Refresh')" :iconLeft="LucideRefreshCcw" @click="reloadAll" />
        <Button v-if="!editing && isAdmin()" :label="__('Edit')" :iconLeft="LucidePenLine" @click="enableEditing" />
        <Button v-if="editing" :label="__('Chart')" iconLeft="plus" @click="showAddChartModal = true" />
        <Button v-if="editing && isAdmin()" :label="__('Reset to default')" :iconLeft="LucideUndo2" @click="resetToDefault" />
        <Button v-if="editing" :label="__('Cancel')" @click="cancel" />
        <Button v-if="editing" variant="solid" :label="__('Save')" :disabled="!dirty" :loading="saveDashboard.loading" @click="save" />
      </template>
    </LayoutHeader>

    <!-- Filters -->
    <div class="p-4 pb-2 flex flex-wrap items-center gap-3 bg-white border-b border-gray-100">
      <Dropdown
        v-if="!showDatePicker"
        :options="dropdownOptions"
        v-model="preset"
        :placeholder="__('Select Range')"
        :button="{ label: __(preset), variant: 'outline', iconRight: 'chevron-down', iconLeft: 'calendar' }"
        class="!w-full max-w-[180px]"
      />
      <DateRangePicker
        v-else ref="datePickerRef" class="!w-44"
        :value="filters.period" variant="outline" :placeholder="__('Period')"
        @change="onDateRangeChange" :formatter="formatRange"
      >
        <template #prefix><LucideCalendar class="size-4 mr-2" style="color:#448DE1" /></template>
      </DateRangePicker>

      <!-- Only admins / managers can switch user -->
      <Link
        v-if="isAdmin() || isManager()"
        class="form-control w-48"
        variant="outline"
        :value="filters.user && getUser(filters.user).full_name"
        doctype="User"
        :filters="{
          name: ['in', users.data.crmUsers?.map((u) => u.name)],
          ignore_user_type: 1,
        }"
        :placeholder="__('Sales User')"
        :hideMe="true"
        @change="(v) => updateFilter('user', v)"
      >
        <template #prefix>
          <UserAvatar v-if="filters.user" class="mr-2" :user="filters.user" size="sm" />
        </template>
        <template #item-prefix="{ option }">
          <UserAvatar class="mr-2" :user="option.value" size="sm" />
        </template>
        <template #item-label="{ option }">
          <Tooltip :text="option.value">
            <div class="cursor-pointer">{{ getUser(option.value).full_name }}</div>
          </Tooltip>
        </template>
      </Link>

      <!-- Sales user: show their name as a read-only badge -->
      <div v-else-if="filters.user" class="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-blue-100 bg-blue-50">
        <UserAvatar :user="filters.user" size="sm" />
        <span class="text-xs font-semibold" style="color:#2D71BF">{{ getUser(filters.user).full_name }}</span>
        <span class="text-[10px] font-bold px-1.5 py-0.5 rounded-full text-white" style="background:#448DE1">My Data</span>
      </div>
    </div>

    <!-- Body -->
    <div class="w-full overflow-y-auto pb-20">
      <div v-if="!editing" class="px-5 mt-6 space-y-10">

        <!-- ══════════════════════════════════════════════════════
             SECTION 1: LEADS PERFORMANCE
        ══════════════════════════════════════════════════════ -->
        <section>
          <div class="flex items-center justify-between mb-5">
            <div class="flex items-center gap-3">
              <div class="size-10 rounded-xl flex items-center justify-center" style="background:#EFF6FF">
                <LucideTarget class="size-5" style="color:#2D71BF" />
              </div>
              <div>
                <h2 class="text-lg font-bold text-gray-900">{{ __('Leads Performance') }}</h2>
                <p class="text-xs" style="color:#A3A3A3">{{ preset }}</p>
              </div>
            </div>
            <!-- Search -->
            <div class="relative w-72">
              <input
                type="text"
                class="w-full pl-9 pr-4 py-2 rounded-lg border text-sm focus:outline-none transition-all"
                style="border-color:#CBE3FF; focus:ring-color:#448DE1"
                :placeholder="__('Search by name or phone...')"
                v-model="filters.searchText"
                @input="debouncedLeadSearch"
              />
              <LucideSearch class="absolute left-3 top-1/2 -translate-y-1/2 size-4" style="color:#A3A3A3" />
            </div>
          </div>

          <!-- Loading / Error / Empty states -->
          <div v-if="leadsData.loading" class="flex items-center justify-center py-16" style="color:#A3A3A3">
            <LucideRefreshCcw class="size-5 animate-spin mr-2" /><span>Loading leads...</span>
          </div>
          <div v-else-if="leadsData.error" class="bg-red-50 border border-red-200 p-8 rounded-xl text-center">
            <p class="text-red-600 text-sm mb-3">{{ leadsData.error?.message || leadsData.error }}</p>
            <button @click="leadsData.reload()" class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700">Retry</button>
          </div>
          <div v-else-if="!leadsData.data?.stats?.total" class="py-16 text-center border border-dashed rounded-xl" style="color:#A3A3A3; border-color:#E5E5E5">
            No leads data for this period
          </div>

          <div v-else class="space-y-6">
            <!-- KPI Row — orange/blue palette -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <!-- Total Leads — Blue -->
              <div class="rounded-2xl p-4 border" style="background:#EFF6FF; border-color:#CBE3FF">
                <div class="flex items-center justify-between mb-2">
                  <div class="size-8 rounded-lg flex items-center justify-center" style="background:#2D71BF">
                    <LucideUsers class="size-4 text-white" />
                  </div>
                  <span class="text-xs font-semibold px-2 py-0.5 rounded-full" style="color:#1A579D; background:#CBE3FF">{{ preset }}</span>
                </div>
                <p class="text-3xl font-black" style="color:#022B59">{{ leadsData.data.stats.total }}</p>
                <p class="text-xs font-semibold uppercase tracking-wide mt-1" style="color:#2D71BF">Total Leads</p>
              </div>
              <!-- Conversion — Orange -->
              <div class="rounded-2xl p-4 border" style="background:#FFF7ED; border-color:#FFDEB6">
                <div class="flex items-center justify-between mb-2">
                  <div class="size-8 rounded-lg flex items-center justify-center" style="background:#B36300">
                    <LucideTrendingUp class="size-4 text-white" />
                  </div>
                  <span class="text-xs font-semibold px-2 py-0.5 rounded-full" style="color:#915100; background:#FFDEB6">Rate</span>
                </div>
                <p class="text-3xl font-black" style="color:#4D2B00">{{ conversionRate }}%</p>
                <p class="text-xs font-semibold uppercase tracking-wide mt-1" style="color:#B36300">Conversion Rate</p>
              </div>
              <!-- Days to Close — Blue light -->
              <div class="rounded-2xl p-4 border" style="background:#EFF6FF; border-color:#A7D0FF">
                <div class="flex items-center justify-between mb-2">
                  <div class="size-8 rounded-lg flex items-center justify-center" style="background:#448DE1">
                    <LucideClock class="size-4 text-white" />
                  </div>
                  <span class="text-xs font-semibold px-2 py-0.5 rounded-full" style="color:#1A579D; background:#A7D0FF">Avg</span>
                </div>
                <p class="text-3xl font-black" style="color:#022B59">{{ leadsData.data.conversion?.avg_days || 0 }}</p>
                <p class="text-xs font-semibold uppercase tracking-wide mt-1" style="color:#448DE1">Days to Close</p>
              </div>
              <!-- Closed Deals — Orange warm -->
              <div class="rounded-2xl p-4 border" style="background:#FFFBEB; border-color:#FFB150">
                <div class="flex items-center justify-between mb-2">
                  <div class="size-8 rounded-lg flex items-center justify-center" style="background:#D57C0C">
                    <LucideStar class="size-4 text-white" />
                  </div>
                  <span class="text-xs font-semibold px-2 py-0.5 rounded-full" style="color:#915100; background:#FFB150">Won</span>
                </div>
                <p class="text-3xl font-black" style="color:#4D2B00">{{ leadsData.data.monthly_target?.won_deals || 0 }}</p>
                <p class="text-xs font-semibold uppercase tracking-wide mt-1" style="color:#D57C0C">Closed Deals</p>
              </div>
            </div>

            <!-- Status Funnel + Donut row -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Status funnel -->
              <div class="bg-white rounded-2xl border p-6" style="border-color:#E5E5E5">
                <h3 class="text-sm font-bold text-gray-900 mb-4">Lead Status Funnel</h3>
                <div v-if="leadsData.data.status_funnel?.length" class="space-y-2">
                  <div v-for="(item, idx) in leadsData.data.status_funnel" :key="item.status" class="flex items-center gap-3 group">
                    <span class="text-xs font-semibold w-32 truncate" style="color:#525252">{{ item.status }}</span>
                    <div class="flex-1 rounded-full h-5 overflow-hidden" style="background:#F5F5F5">
                      <div class="h-full rounded-full transition-all duration-700 flex items-center justify-end pr-2"
                        :style="{ width: Math.max(item.pct, 2) + '%', backgroundColor: chartColor(item.status, idx) }">
                        <span class="text-[9px] font-black text-white" v-if="item.pct > 10">{{ item.count }}</span>
                      </div>
                    </div>
                    <span class="text-xs font-black w-8 text-right" style="color:#404040">{{ item.count }}</span>
                    <span class="text-[10px] w-10 text-right" style="color:#A3A3A3">{{ item.pct }}%</span>
                  </div>
                </div>
                <div v-else class="py-8 text-center text-sm" style="color:#A3A3A3">No status data</div>
              </div>

              <!-- Pipeline Donut -->
              <div class="bg-white rounded-2xl border p-6" style="border-color:#E5E5E5">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-sm font-bold text-gray-900">Pipeline Distribution</h3>
                  <span class="text-xs" style="color:#A3A3A3">{{ leadsData.data.stats.total }} leads</span>
                </div>
                <div class="flex items-center gap-6">
                  <div class="relative size-40 shrink-0" v-if="donutHasData">
                    <svg viewBox="0 0 120 120" class="w-full h-full -rotate-90" style="filter:drop-shadow(0 2px 8px rgba(2,43,89,0.10))">
                      <defs>
                        <filter id="seg-shadow" x="-20%" y="-20%" width="140%" height="140%">
                          <feDropShadow dx="0" dy="1" stdDeviation="1.5" flood-color="#022B59" flood-opacity="0.12"/>
                        </filter>
                      </defs>
                      <!-- Track ring -->
                      <circle cx="60" cy="60" r="46" fill="none" stroke="#EFF6FF" stroke-width="18" />
                      <!-- Segments — 1px gap via dash trick -->
                      <circle v-for="seg in donutSegments" :key="seg.status"
                        cx="60" cy="60" r="46" fill="none"
                        :stroke="seg.color" stroke-width="18"
                        :stroke-dasharray="`${Math.max(seg.dash - 2, 0)} ${seg.gap + 2}`"
                        :stroke-dashoffset="seg.offset"
                        stroke-linecap="round"
                        filter="url(#seg-shadow)"
                        class="transition-all duration-1000 ease-out"
                      />
                    </svg>
                    <!-- Centre label -->
                    <div class="absolute inset-0 flex flex-col items-center justify-center">
                      <span class="text-2xl font-black leading-none" style="color:#022B59">{{ leadsData.data.monthly_target?.won_deals || 0 }}</span>
                      <span class="text-[9px] font-bold uppercase tracking-widest mt-0.5" style="color:#A3A3A3">Won</span>
                    </div>
                  </div>
                  <div v-else class="size-40 flex items-center justify-center rounded-full border-2 border-dashed" style="background:#FAFAFA; border-color:#E5E5E5">
                    <span class="text-xs" style="color:#A3A3A3">No data</span>
                  </div>
                  <div class="flex-1 grid grid-cols-1 gap-1.5 overflow-y-auto max-h-40">
                    <div v-for="seg in donutSegments.slice(0,7)" :key="seg.status"
                      class="flex items-center gap-2 px-2 py-1 rounded-lg transition-all hover:opacity-80"
                      :style="{ background: seg.color + '18' }">
                      <span class="size-3 rounded-sm shrink-0 shadow-sm" :style="{ background: seg.color }"></span>
                      <span class="text-xs truncate font-medium" style="color:#404040">{{ seg.status }}</span>
                      <span class="text-xs font-black ml-auto" style="color:#171717">{{ seg.count }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Activities + Status Grid -->
            <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
              <!-- Activities -->
              <div class="bg-white rounded-2xl border p-6" style="border-color:#E5E5E5">
                <h3 class="text-sm font-bold text-gray-900 mb-4">Activity Breakdown</h3>
                <div class="grid grid-cols-2 gap-3">
                  <div v-for="act in activityItems" :key="act.key"
                    class="flex flex-col items-center p-3 rounded-xl border hover:bg-white transition-all group"
                    style="border-color:#E5E5E5; background:#FAFAFA">
                    <div class="size-9 rounded-lg mb-2 flex items-center justify-center transition-transform group-hover:scale-110" :style="{ background: act.bg }">
                      <component :is="act.icon" class="size-4" :style="{ color: act.color }" />
                    </div>
                    <span class="text-lg font-black" style="color:#171717">{{ leadsData.data.activities?.[act.key] ?? 0 }}</span>
                    <span class="text-[9px] font-bold uppercase" style="color:#A3A3A3">{{ act.label }}</span>
                  </div>
                </div>
              </div>

              <!-- Leads by Status cards -->
              <div class="bg-white rounded-2xl border p-6 xl:col-span-2" style="border-color:#E5E5E5">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-sm font-bold text-gray-900">Leads by Status</h3>
                  <RouterLink :to="{ name: 'Leads', query: buildLeadQuery() }" class="text-xs flex items-center gap-1 hover:opacity-80" style="color:#2D71BF">
                    View all <LucideArrowRight class="size-3" />
                  </RouterLink>
                </div>
                <div class="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
                  <RouterLink v-for="item in leadOverviewCards" :key="item.status"
                    :to="{ name: 'Leads', query: buildLeadQuery({ status: item.db_status }) }"
                    class="flex flex-col items-center p-3 rounded-xl border hover:shadow-sm hover:-translate-y-0.5 transition-all group bg-white"
                    style="border-color:#E5E5E5">
                    <div class="size-9 rounded-lg mb-2 flex items-center justify-center" :style="{ background: item.bg }">
                      <component :is="item.icon" class="size-5" :style="{ color: item.color }" />
                    </div>
                    <span class="text-xl font-black group-hover:text-blue-600" style="color:#171717">{{ item.count }}</span>
                    <span class="text-[9px] font-bold text-center uppercase mt-0.5 leading-none" style="color:#A3A3A3">{{ __(item.status) }}</span>
                  </RouterLink>
                </div>
              </div>
            </div>

            <!-- Lost Reasons + Sources -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Lost Reasons -->
              <div class="bg-white rounded-2xl border p-6" style="border-color:#E5E5E5">
                <div class="flex items-center justify-between mb-5 pb-4 border-b" style="border-color:#F5F5F5">
                  <h3 class="text-sm font-bold text-gray-900 flex items-center gap-2">
                    <LucideXCircle class="size-4 text-red-500" /> Lost Reasons
                  </h3>
                  <div class="flex gap-3 text-xs" style="color:#A3A3A3">
                    <span class="flex items-center gap-1">
                      <span class="size-2 rounded-full" style="background:#448DE1"></span>{{ conversionRate }}% won
                    </span>
                    <span class="flex items-center gap-1">
                      <span class="size-2 rounded-full bg-red-400"></span>{{ lostPct }}% lost
                    </span>
                  </div>
                </div>
                <div v-if="lostReasonChartData.length" class="flex items-end gap-3 h-52">
                  <div v-for="item in lostReasonChartData" :key="item.reason"
                    class="flex-1 flex flex-col items-center justify-end h-full group">
                    <span class="text-xs font-bold mb-1" style="color:#525252">{{ item.count }}</span>
                    <div class="w-full rounded-t-lg transition-all duration-700 origin-bottom group-hover:scale-x-105"
                      :style="{ height: item.heightPct + '%', backgroundColor: item.color }"></div>
                    <p class="text-[9px] font-semibold mt-2 text-center uppercase leading-none truncate w-full" style="color:#A3A3A3">{{ item.reason }}</p>
                  </div>
                </div>
                <div v-else class="py-10 text-center text-sm rounded-xl" style="color:#A3A3A3; background:#FAFAFA">No lost reasons recorded</div>
              </div>

              <!-- Source Performance -->
              <div class="bg-white rounded-2xl border p-6" style="border-color:#E5E5E5">
                <div class="flex items-center justify-between mb-5 pb-4 border-b" style="border-color:#F5F5F5">
                  <h3 class="text-sm font-bold text-gray-900 flex items-center gap-2">
                    <LucideBarChart2 class="size-4" style="color:#448DE1" /> Source Performance
                  </h3>
                  <div class="flex gap-3 text-xs" style="color:#A3A3A3">
                    <span class="flex items-center gap-1">
                      <span class="size-2 rounded-full" style="background:#2D71BF"></span>Total
                    </span>
                    <span class="flex items-center gap-1">
                      <span class="size-2 rounded-full" style="background:#F7961D"></span>Won
                    </span>
                  </div>
                </div>
                <div v-if="leadSourcesChartData.length" class="flex items-end justify-around gap-4 h-52">
                  <div v-for="item in leadSourcesChartData" :key="item.source"
                    class="flex flex-col items-center justify-end h-full group">
                    <div class="flex gap-1.5 items-end h-full">
                      <div class="w-3 rounded-t-full shadow-sm transition-all duration-1000 origin-bottom relative"
                        :style="{ height: item.totalHeight + '%', background: '#2D71BF' }">
                        <div class="absolute -top-7 left-1/2 -translate-x-1/2 text-white text-[9px] px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap"
                          style="background:#022B59">
                          {{ item.total }}
                        </div>
                      </div>
                      <div class="w-3 rounded-t-full shadow-sm transition-all duration-1000 origin-bottom"
                        :style="{ height: item.wonHeight + '%', background: '#F7961D' }"></div>
                    </div>
                    <span class="text-[9px] font-bold mt-2 text-center uppercase" style="color:#525252">{{ item.source }}</span>
                  </div>
                </div>
                <div v-else class="py-10 text-center text-sm rounded-xl" style="color:#A3A3A3; background:#FAFAFA">No source data</div>
              </div>
            </div>
          </div>
        </section>

        <!-- ══════════════════════════════════════════════════════
             SECTION 2: Inventory PERFORMANCE
        ══════════════════════════════════════════════════════ -->
        <section class="border-t pt-8" style="border-color:#F5F5F5">
          <div class="flex items-center gap-3 mb-5">
            <div class="size-10 rounded-xl flex items-center justify-center" style="background:#FFF7ED">
              <LucideLayoutGrid class="size-5" style="color:#D57C0C" />
            </div>
            <div>
              <h2 class="text-lg font-bold text-gray-900">{{ __('Inventory Performance') }}</h2>
              <p class="text-xs" style="color:#A3A3A3">Live inventory data</p>
            </div>
          </div>

          <div v-if="inventoryData.loading" class="flex items-center justify-center py-16" style="color:#A3A3A3">
            <LucideRefreshCcw class="size-5 animate-spin mr-2" /><span>Loading inventory...</span>
          </div>
          <div v-else-if="inventoryData.error" class="bg-red-50 border border-red-200 p-8 rounded-xl text-center">
            <p class="text-red-600 text-sm mb-3">{{ inventoryData.error?.message || inventoryData.error }}</p>
            <button @click="inventoryData.reload()" class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700">Retry</button>
          </div>

          <div v-else class="space-y-6">
            <!-- Overview cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Projects — Blue scale -->
              <div class="rounded-2xl p-6 border" style="background:linear-gradient(135deg,#EFF6FF,#fff); border-color:#CBE3FF">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-sm font-bold text-gray-900 flex items-center gap-2">
                    <LucideBuilding2 class="size-5" style="color:#2D71BF" /> Projects
                  </h3>
                  <span class="text-xs font-bold px-2 py-0.5 rounded-full" style="color:#1A579D; background:#CBE3FF">
                    {{ inventoryData.data.project_stats?.total || 0 }}
                  </span>
                </div>
                <div class="grid grid-cols-4 gap-3">
                  <div class="text-center p-3 rounded-xl bg-white border" style="border-color:#E5E5E5">
                    <p class="text-2xl font-black" style="color:#171717">{{ inventoryData.data.project_stats?.total || 0 }}</p>
                    <p class="text-[10px] font-semibold uppercase mt-1" style="color:#A3A3A3">Total</p>
                  </div>
                  <div class="text-center p-3 rounded-xl border" style="background:#EFF6FF; border-color:#CBE3FF">
                    <p class="text-2xl font-black" style="color:#2D71BF">{{ inventoryData.data.project_stats?.available || 0 }}</p>
                    <p class="text-[10px] font-semibold uppercase mt-1" style="color:#448DE1">Active</p>
                  </div>
                  <div class="text-center p-3 rounded-xl border" style="background:#FFF7ED; border-color:#FFDEB6">
                    <p class="text-2xl font-black" style="color:#B36300">{{ inventoryData.data.project_stats?.sold || 0 }}</p>
                    <p class="text-[10px] font-semibold uppercase mt-1" style="color:#D57C0C">Sold</p>
                  </div>
                  <div class="text-center p-3 rounded-xl border" style="background:#FAFAFA; border-color:#E5E5E5">
                    <p class="text-2xl font-black" style="color:#737373">{{ inventoryData.data.project_stats?.archived || 0 }}</p>
                    <p class="text-[10px] font-semibold uppercase mt-1" style="color:#A3A3A3">Archived</p>
                  </div>
                </div>
              </div>
              <!-- Units — Orange scale -->
              <div class="rounded-2xl p-6 border" style="background:linear-gradient(135deg,#FFF7ED,#fff); border-color:#FFB150">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-sm font-bold text-gray-900 flex items-center gap-2">
                    <LucideHome class="size-5" style="color:#D57C0C" /> Units
                  </h3>
                  <span class="text-xs font-bold px-2 py-0.5 rounded-full" style="color:#915100; background:#FFDEB6">
                    {{ inventoryData.data.unit_stats?.total || 0 }}
                  </span>
                </div>
                <div class="grid grid-cols-4 gap-3">
                  <div class="text-center p-3 rounded-xl bg-white border" style="border-color:#E5E5E5">
                    <p class="text-2xl font-black" style="color:#171717">{{ inventoryData.data.unit_stats?.total || 0 }}</p>
                    <p class="text-[10px] font-semibold uppercase mt-1" style="color:#A3A3A3">Total</p>
                  </div>
                  <div class="text-center p-3 rounded-xl border" style="background:#FFF7ED; border-color:#FFDEB6">
                    <p class="text-2xl font-black" style="color:#B36300">{{ inventoryData.data.unit_stats?.available || 0 }}</p>
                    <p class="text-[10px] font-semibold uppercase mt-1" style="color:#D57C0C">Available</p>
                  </div>
                  <div class="text-center p-3 rounded-xl border" style="background:#EFF6FF; border-color:#CBE3FF">
                    <p class="text-2xl font-black" style="color:#2D71BF">{{ inventoryData.data.unit_stats?.sold || 0 }}</p>
                    <p class="text-[10px] font-semibold uppercase mt-1" style="color:#448DE1">Sold</p>
                  </div>
                  <div class="text-center p-3 rounded-xl border" style="background:#FFFBEB; border-color:#FFC883">
                    <p class="text-2xl font-black" style="color:#915100">{{ inventoryData.data.unit_stats?.reserved || 0 }}</p>
                    <p class="text-[10px] font-semibold uppercase mt-1" style="color:#D57C0C">Reserved</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Insights -->
            <div v-if="inventoryData.data.insights?.length" class="bg-white rounded-2xl border p-6" style="border-color:#E5E5E5">
              <h3 class="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
                <LucideLightbulb class="size-5" style="color:#D57C0C" /> Key Insights
              </h3>
              <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <div v-for="ins in inventoryData.data.insights" :key="ins.label"
                  class="p-4 rounded-xl border transition-all hover:bg-white"
                  style="background:#FAFAFA; border-color:#E5E5E5">
                  <p class="text-[10px] font-bold uppercase mb-1" style="color:#A3A3A3">{{ ins.label }}</p>
                  <p class="text-base font-black" style="color:#171717">{{ ins.value }}</p>
                  <p class="text-[10px] mt-0.5 italic" style="color:#A3A3A3">{{ ins.sub }}</p>
                </div>
              </div>
            </div>

            <!-- Project donuts -->
            <div v-if="inventoryPerformanceData.length" class="grid grid-cols-1 md:grid-cols-3 gap-5">
              <div v-for="proj in inventoryPerformanceData" :key="proj.project"
                class="bg-white rounded-2xl border p-5 hover:shadow-lg transition-all" style="border-color:#E5E5E5">
                <h4 class="text-xs font-bold uppercase mb-4 pb-3 border-b" style="color:#525252; border-color:#F5F5F5">{{ proj.project }}</h4>
                <div class="flex items-center gap-4">
                  <div class="relative size-24 shrink-0">
                    <svg viewBox="0 0 100 100" class="size-full -rotate-90">
                      <circle cx="50" cy="50" r="40" fill="none" stroke="#F5F5F5" stroke-width="12" />
                      <circle cx="50" cy="50" r="40" fill="none" stroke="#2D71BF" stroke-width="12"
                        :stroke-dasharray="`${(proj.sold/Math.max(proj.total,1))*251.2} 251.2`"
                        stroke-linecap="round" class="transition-all duration-1000" />
                    </svg>
                    <div class="absolute inset-0 flex flex-col items-center justify-center">
                      <span class="text-lg font-black" style="color:#022B59">{{ proj.percent }}%</span>
                      <span class="text-[8px] font-bold uppercase" style="color:#A3A3A3">Sold</span>
                    </div>
                  </div>
                  <div class="flex-1 space-y-2">
                    <div>
                      <div class="flex items-center gap-1.5 mb-0.5">
                        <div class="size-2 rounded-full" style="background:#2D71BF"></div>
                        <span class="text-[10px] font-bold" style="color:#525252">Sold</span>
                      </div>
                      <span class="text-base font-black pl-3.5" style="color:#022B59">{{ proj.sold }}</span>
                    </div>
                    <div>
                      <div class="flex items-center gap-1.5 mb-0.5">
                        <div class="size-2 rounded-full" style="background:#83BDFF"></div>
                        <span class="text-[10px] font-bold" style="color:#A3A3A3">Available</span>
                      </div>
                      <span class="text-base font-black pl-3.5" style="color:#737373">{{ proj.total - proj.sold }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Profits + Reservations -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div class="bg-white rounded-2xl border p-6" style="border-color:#E5E5E5">
                <div class="flex items-center justify-between mb-5">
                  <h3 class="text-sm font-bold text-gray-900">Expected vs Realized Profits</h3>
                  <span class="text-xs px-3 py-1 rounded-full" style="color:#2D71BF; background:#EFF6FF">{{ currentMonth }}</span>
                </div>
                <div class="flex items-end justify-between gap-4 h-48">
                  <div v-for="(item, idx) in inventoryProfitsData" :key="idx"
                    class="flex-1 flex flex-col items-center justify-end h-full group">
                    <span class="text-sm font-bold mb-2 group-hover:-translate-y-1 transition-transform" :style="{ color: item.color }">{{ item.value || 0 }}K</span>
                    <div class="w-full rounded-t-xl shadow-sm transition-all duration-1000 origin-bottom"
                      :style="{ height: profitBarHeight(item.value) + '%', background: item.color }"></div>
                    <span class="text-xs font-bold mt-3 uppercase" style="color:#525252">{{ item.type }}</span>
                  </div>
                </div>
              </div>
              <div class="bg-white rounded-2xl border p-6" style="border-color:#E5E5E5">
                <div class="flex items-center justify-between mb-5">
                  <h3 class="text-sm font-bold text-gray-900">Reservation Status</h3>
                  <span class="text-xs px-3 py-1 rounded-full" style="color:#B36300; background:#FFF7ED">{{ currentMonth }}</span>
                </div>
                <div class="flex items-end justify-between gap-4 h-48">
                  <div v-for="(item, idx) in inventoryReservationsData" :key="idx"
                    class="flex-1 flex flex-col items-center justify-end h-full group">
                    <span class="text-sm font-bold mb-2 group-hover:-translate-y-1 transition-transform" :style="{ color: item.color }">{{ item.value || 0 }}</span>
                    <div class="w-full rounded-t-xl shadow-sm transition-all duration-1000 origin-bottom"
                      :style="{ height: reservationBarHeight(item.value) + '%', background: item.color }"></div>
                    <span class="text-xs font-bold mt-3 uppercase" style="color:#525252">{{ item.type }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- ══════════════════════════════════════════════════════
             SECTION 3: TASKS PERFORMANCE
        ══════════════════════════════════════════════════════ -->
        <section class="border-t pt-8 pb-8" style="border-color:#F5F5F5">
          <div class="flex items-center gap-3 mb-5">
            <div class="size-10 rounded-xl flex items-center justify-center" style="background:#FFFBEB">
              <LucideCalendarCheck class="size-5" style="color:#D57C0C" />
            </div>
            <div>
              <h2 class="text-lg font-bold text-gray-900">{{ __('Tasks Performance') }}</h2>
              <p class="text-xs" style="color:#A3A3A3">Calls, meetings, showings & more</p>
            </div>
          </div>

          <div v-if="tasksData.loading" class="flex items-center justify-center py-16" style="color:#A3A3A3">
            <LucideRefreshCcw class="size-5 animate-spin mr-2" /><span>Loading tasks...</span>
          </div>
          <div v-else-if="tasksData.error" class="bg-red-50 border border-red-200 p-8 rounded-xl text-center">
            <p class="text-red-600 text-sm mb-3">{{ tasksData.error?.message || tasksData.error }}</p>
            <button @click="tasksData.reload()" class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700">Retry</button>
          </div>

          <div v-else class="space-y-6">
            <!-- Task KPIs -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="rounded-2xl p-4 border" style="background:#EFF6FF; border-color:#CBE3FF">
                <div class="flex items-center justify-between mb-2">
                  <div class="size-8 rounded-lg flex items-center justify-center" style="background:#2D71BF">
                    <LucideCheckCircle class="size-4 text-white" />
                  </div>
                  <span class="text-xs font-semibold px-2 py-0.5 rounded-full" style="color:#1A579D; background:#CBE3FF">Total</span>
                </div>
                <p class="text-3xl font-black" style="color:#022B59">{{ tasksData.data?.kpis?.total || 0 }}</p>
                <p class="text-xs font-semibold uppercase tracking-wide mt-1" style="color:#2D71BF">All Tasks</p>
              </div>
              <div class="rounded-2xl p-4 border" style="background:#FFF7ED; border-color:#FFDEB6">
                <div class="flex items-center justify-between mb-2">
                  <div class="size-8 rounded-lg flex items-center justify-center" style="background:#D57C0C">
                    <LucideTrendingUp class="size-4 text-white" />
                  </div>
                  <span class="text-xs font-semibold px-2 py-0.5 rounded-full" style="color:#915100; background:#FFB150">Rate</span>
                </div>
                <p class="text-3xl font-black" style="color:#4D2B00">{{ tasksData.data?.kpis?.completion_rate || 0 }}%</p>
                <p class="text-xs font-semibold uppercase tracking-wide mt-1" style="color:#D57C0C">Completion Rate</p>
              </div>
              <div class="rounded-2xl p-4 border" style="background:#FEF2F2; border-color:#FECACA">
                <div class="flex items-center justify-between mb-2">
                  <div class="size-8 rounded-lg bg-red-500 flex items-center justify-center">
                    <LucideAlertCircle class="size-4 text-white" />
                  </div>
                  <span class="text-xs font-semibold text-red-700 bg-red-100 px-2 py-0.5 rounded-full">Alert</span>
                </div>
                <p class="text-3xl font-black text-red-900">{{ tasksData.data?.kpis?.late || 0 }}</p>
                <p class="text-xs font-semibold text-red-700 uppercase tracking-wide mt-1">Overdue Tasks</p>
              </div>
              <div class="rounded-2xl p-4 border" style="background:#EFF6FF; border-color:#A7D0FF">
                <div class="flex items-center justify-between mb-2">
                  <div class="size-8 rounded-lg flex items-center justify-center" style="background:#448DE1">
                    <LucideClock class="size-4 text-white" />
                  </div>
                  <span class="text-xs font-semibold px-2 py-0.5 rounded-full" style="color:#1A579D; background:#A7D0FF">Active</span>
                </div>
                <p class="text-3xl font-black" style="color:#022B59">{{ tasksData.data?.kpis?.in_progress || 0 }}</p>
                <p class="text-xs font-semibold uppercase tracking-wide mt-1" style="color:#448DE1">In Progress</p>
              </div>
            </div>

            <!-- Status + Type + Priority -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div v-for="(panel, pKey) in taskBreakdownPanels" :key="pKey"
                class="bg-white rounded-2xl border p-6" style="border-color:#E5E5E5">
                <h3 class="text-sm font-bold text-gray-900 mb-4">{{ panel.title }}</h3>
                <div class="space-y-3">
                  <div v-for="item in panel.items" :key="item[panel.key]" class="flex items-center gap-3">
                    <span class="size-2.5 rounded-full shrink-0" :style="{ background: item.color }"></span>
                    <span class="text-xs flex-1 capitalize" style="color:#525252">{{ item[panel.key] }}</span>
                    <div class="w-20 rounded-full h-1.5" style="background:#F5F5F5">
                      <div class="h-full rounded-full" :style="{ width: item.pct + '%', backgroundColor: item.color }"></div>
                    </div>
                    <span class="text-xs font-bold w-8 text-right" style="color:#404040">{{ item.count }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Task type performance table -->
            <div class="bg-white rounded-2xl border p-6" style="border-color:#E5E5E5">
              <h3 class="text-sm font-bold text-gray-900 mb-4">Task Type Performance</h3>
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="border-b" style="border-color:#F5F5F5">
                      <th class="text-left text-[10px] font-bold uppercase pb-3 pr-4" style="color:#A3A3A3">Type</th>
                      <th class="text-right text-[10px] font-bold uppercase pb-3 px-4" style="color:#A3A3A3">Total</th>
                      <th class="text-right text-[10px] font-bold uppercase pb-3 px-4" style="color:#A3A3A3">Done</th>
                      <th class="text-right text-[10px] font-bold uppercase pb-3 px-4" style="color:#A3A3A3">Late</th>
                      <th class="text-right text-[10px] font-bold uppercase pb-3 pl-4" style="color:#A3A3A3">Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in tasksData.data?.type_performance || []" :key="item.type"
                      class="border-b hover:bg-gray-50 transition-colors" style="border-color:#FAFAFA">
                      <td class="py-3 pr-4">
                        <div class="flex items-center gap-2">
                          <span class="size-2 rounded-full" :style="{ background: item.color }"></span>
                          <span class="text-xs capitalize" style="color:#404040">{{ item.type }}</span>
                        </div>
                      </td>
                      <td class="text-right text-xs font-semibold px-4" style="color:#404040">{{ item.total }}</td>
                      <td class="text-right text-xs font-semibold px-4" style="color:#B36300">{{ item.done }}</td>
                      <td class="text-right text-xs font-semibold text-red-500 px-4">{{ item.late }}</td>
                      <td class="text-right pl-4">
                        <span class="text-xs font-bold px-2 py-0.5 rounded-full"
                          :style="item.completion_rate >= 70
                            ? { background:'#EFF6FF', color:'#2D71BF' }
                            : item.completion_rate >= 40
                              ? { background:'#FFF7ED', color:'#D57C0C' }
                              : { background:'#FEF2F2', color:'#DC2626' }">
                          {{ item.completion_rate }}%
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Completion by user -->
            <div v-if="tasksData.data?.completion_by_user?.length" class="bg-white rounded-2xl border p-6" style="border-color:#E5E5E5">
              <h3 class="text-sm font-bold text-gray-900 mb-4">Completion by Team Member</h3>
              <div class="space-y-3">
                <div v-for="item in tasksData.data.completion_by_user" :key="item.user"
                  class="flex items-center gap-4">
                  <UserAvatar :user="item.user" size="sm" class="shrink-0" />
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-xs font-semibold truncate" style="color:#404040">{{ item.name }}</span>
                      <span class="text-xs font-bold ml-2"
                        :style="item.completion_rate >= 70
                          ? { color:'#2D71BF' }
                          : item.completion_rate >= 40
                            ? { color:'#D57C0C' }
                            : { color:'#DC2626' }">
                        {{ item.completion_rate }}%
                      </span>
                    </div>
                    <div class="w-full rounded-full h-1.5" style="background:#F5F5F5">
                      <div class="h-full rounded-full transition-all duration-700"
                        :style="{
                          width: item.completion_rate + '%',
                          background: item.completion_rate >= 70 ? '#448DE1'
                                    : item.completion_rate >= 40 ? '#F7961D'
                                    : '#EF4444'
                        }"></div>
                    </div>
                  </div>
                  <div class="flex gap-3 text-[10px] shrink-0" style="color:#A3A3A3">
                    <span class="flex items-center gap-1"><span class="size-1.5 rounded-full" style="background:#448DE1"></span>{{ item.done }}</span>
                    <span class="flex items-center gap-1"><span class="size-1.5 rounded-full bg-red-400"></span>{{ item.late }}</span>
                    <span class="font-semibold" style="color:#525252">/ {{ item.total }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AddChartModal from '@/components/Dashboard/AddChartModal.vue'
import DashboardGrid from '@/components/Dashboard/DashboardGrid.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import Link from '@/components/Controls/Link.vue'

import LucideRefreshCcw     from '~icons/lucide/refresh-ccw'
import LucideUndo2          from '~icons/lucide/undo-2'
import LucidePenLine        from '~icons/lucide/pen-line'
import LucideCalendar       from '~icons/lucide/calendar'
import LucideUsers          from '~icons/lucide/users'
import LucideActivity       from '~icons/lucide/activity'
import LucideClock          from '~icons/lucide/clock'
import LucideTrendingUp     from '~icons/lucide/trending-up'
import LucideTarget         from '~icons/lucide/target'
import LucideXCircle        from '~icons/lucide/x-circle'
import LucideSearch         from '~icons/lucide/search'
import LucideArrowRight     from '~icons/lucide/arrow-right'
import LucideBarChart2      from '~icons/lucide/bar-chart-2'
import LucidePhone          from '~icons/lucide/phone'
import LucidePhoneForwarded from '~icons/lucide/phone-forwarded'
import LucideMessageSquare  from '~icons/lucide/message-square'
import LucideMessageCircle  from '~icons/lucide/message-circle'
import LucideMail           from '~icons/lucide/mail'
import LucideCalendarCheck  from '~icons/lucide/calendar-check'
import LucideEye            from '~icons/lucide/eye'
import LucideBookmark       from '~icons/lucide/bookmark'
import LucideStar           from '~icons/lucide/star'
import LucideCheckCircle    from '~icons/lucide/check-circle'
import LucideAlertCircle    from '~icons/lucide/alert-circle'
import LucideLayoutGrid     from '~icons/lucide/layout-grid'
import LucideThumbsDown     from '~icons/lucide/thumbs-down'
import LucideBuilding2      from '~icons/lucide/building-2'
import LucideHome           from '~icons/lucide/home'
import LucideLightbulb      from '~icons/lucide/lightbulb'

import { usersStore } from '@/stores/users'
import { copy } from '@/utils'
import { getLastXDays, formatter, formatRange } from '@/utils/dashboard'
import { usePageMeta, createResource, DateRangePicker, Dropdown, Tooltip } from 'frappe-ui'
import { ref, reactive, computed, provide, onMounted, onUnmounted } from 'vue'

const { users, getUser, isManager, isAdmin } = usersStore()

// ── Sales-user auto-scope ──────────────────────────────────────────────────────
// If the current session user is neither admin nor manager, lock the user filter
// to their own account so they only see their own data.
const isSalesUser = computed(() => !isAdmin() && !isManager())

const editing = ref(false)
const showDatePicker = ref(false)
const datePickerRef = ref<any>(null)
const preset = ref('Last 30 Days')
const showAddChartModal = ref(false)

type FilterKey = 'period' | 'user' | 'project' | 'status' | 'searchText'
const filters = reactive<Record<FilterKey, any>>({
  period:     getLastXDays(),
  user:       null,
  project:    null,
  status:     null,
  searchText: '',
})

// On mount: lock sales users to their own data immediately
onMounted(() => {
  if (isSalesUser.value) {
    // frappe.session.user is the authenticated Frappe user
    const sessionUser = (window as any)?.frappe?.session?.user ?? null
    if (sessionUser && sessionUser !== 'Administrator') {
      filters.user = sessionUser
    }
  }
})

const fromDate    = computed(() => filters.period?.split(',')[0] ?? null)
const toDate      = computed(() => filters.period?.split(',')[1] ?? null)
const currentMonth = computed(() => new Date().toLocaleString('default', { month: 'long' }))

// ── Reload helpers ─────────────────────────────────────────────────────────────
function reloadAll() {
  dashboardItems.reload()
  leadsData.reload()
  inventoryData.reload()
  tasksData.reload()
}

function reloadLeads() { leadsData.reload() }

let searchTimeout: ReturnType<typeof setTimeout> | null = null
function debouncedLeadSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(reloadLeads, 500)
}
onUnmounted(() => { if (searchTimeout) clearTimeout(searchTimeout) })

function updateFilter(key: FilterKey, value: any) {
  // Prevent sales users from changing the user filter
  if (key === 'user' && isSalesUser.value) return
  filters[key] = value
  reloadAll()
}

function onDateRangeChange(v: string | null) {
  if (!v) {
    showDatePicker.value = false
    filters.period = getLastXDays()
    preset.value = 'Last 30 Days'
  } else {
    filters.period = v
    preset.value = formatter(v)
    showDatePicker.value = false
  }
  reloadAll()
}

const dropdownOptions = computed(() => [
  {
    group: 'Presets', hideLabel: true,
    items: [7, 30, 60, 90].map((days) => ({
      label: `Last ${days} Days`,
      onClick: () => { preset.value = `Last ${days} Days`; filters.period = getLastXDays(days); reloadAll() },
    })),
  },
  {
    label: 'Custom Range',
    onClick: () => { showDatePicker.value = true; preset.value = 'Custom Range'; setTimeout(() => datePickerRef.value?.open(), 0) },
  },
])

// ── Resources ──────────────────────────────────────────────────────────────────
const dashboardItems = createResource({
  url: 'crm.api.dashboard.get_dashboard',
  makeParams() { return { from_date: fromDate.value, to_date: toDate.value, user: filters.user } },
  auto: true,
})

const leadsData = createResource({
  url: 'crm.api.dashboard.get_leads_dashboard',
  makeParams() {
    return {
      from_date: fromDate.value,
      to_date:   toDate.value,
      user:      filters.user,
      project:   filters.project,
      status:    filters.status,
      search:    filters.searchText,
    }
  },
  auto: true,
})

const inventoryData = createResource({
  url: 'crm.api.dashboard.get_inventory_dashboard',
  makeParams() { return { from_date: fromDate.value, to_date: toDate.value, user: filters.user, project: filters.project } },
  auto: true,
})

const tasksData = createResource({
  url: 'crm.api.dashboard.get_tasks_dashboard',
  makeParams() { return { from_date: fromDate.value, to_date: toDate.value, user: filters.user, project: filters.project } },
  auto: true,
})

// ── Editing ────────────────────────────────────────────────────────────────────
const oldItems = ref<any[]>([])
const dirty = computed(() => editing.value && JSON.stringify(dashboardItems.data) !== JSON.stringify(oldItems.value))

provide('fromDate', fromDate)
provide('toDate', toDate)
provide('filters', filters)

function enableEditing() { editing.value = true; oldItems.value = copy(dashboardItems.data) }
function cancel()        { editing.value = false; dashboardItems.data = copy(oldItems.value) }

const saveDashboard = createResource({
  url: 'frappe.client.set_value', method: 'POST',
  onSuccess: () => { dashboardItems.reload(); editing.value = false },
})

function save() {
  const items = copy(dashboardItems.data)
  items.forEach((item: any) => { delete item.data })
  saveDashboard.submit({ doctype: 'CRM Dashboard', name: 'Manager Dashboard', fieldname: 'layout', value: JSON.stringify(items) })
}

function resetToDefault() {
  createResource({ url: 'crm.api.dashboard.reset_to_default', auto: true, onSuccess: () => { dashboardItems.reload(); editing.value = false } })
}

// ── Color palette (from design system) ────────────────────────────────────────
// Blue  : #022B59 #0C407B #1A579D #2D71BF #448DE1 #5FA9FF #83BDFF #A7D0FF #CBE3FF #EFF6FF
// Orange: #4D2B00 #6F3E00 #915100 #B36300 #D57C0C #F7961D #FFB150 #FFC883 #FFDEB6 (50≈same)
// Gray  : #0A0A0A #171717 #262626 #404040 #525252 #737373 #A3A3A3 #D4D4D4 #E5E5E5 #F5F5F5 #FAFAFA

// ── Leads computed ─────────────────────────────────────────────────────────────
const conversionRate = computed<number>(() => {
  const stats = leadsData.data?.stats
  if (!stats || stats.total === 0) return 0
  const won = leadsData.data?.monthly_target?.won_deals ?? 0
  return parseFloat(((won / stats.total) * 100).toFixed(1))
})

const lostPct = computed<string>(() => (100 - conversionRate.value).toFixed(1))

// ── Design-system color palettes ──────────────────────────────────────────────
// Professional sequential palette — alternating Blue & Orange families.
// These are used for ALL chart segments; server-supplied colors are IGNORED.
const DONUT_COLOURS = [
  '#1A579D', // Blue-700   — deep anchor
  '#B36300', // Orange-600 — warm contrast
  '#448DE1', // Blue-500   — mid blue
  '#FFB150', // Orange-400 — soft amber
  '#5FA9FF', // Blue-400   — sky
  '#D57C0C', // Orange-500 — golden
  '#83BDFF', // Blue-300   — light blue
  '#FFC883', // Orange-300 — peach
  '#A7D0FF', // Blue-200   — pale blue
  '#FFDEB6', // Orange-200 — pale amber
]

// Per-status fixed mapping so the same status always gets the same hue
const STATUS_COLOR_MAP: Record<string, string> = {
  'New':                  '#1A579D',
  'Contacted':            '#B36300',
  'Nurture':              '#448DE1',
  'Qualified':            '#FFB150',
  'Meeting':              '#5FA9FF',
  'Junk':                 '#D57C0C',
  'Unqualified':          '#83BDFF',
  'Follow Up To Meeting': '#FFC883',
  'Reserved':             '#A7D0FF',
  'Lost':                 '#FFDEB6',
}

function chartColor(status: string, idx: number): string {
  return STATUS_COLOR_MAP[status] ?? DONUT_COLOURS[idx % DONUT_COLOURS.length]
}

const CIRCUMFERENCE = 2 * Math.PI * 46
const donutHasData  = computed(() => (leadsData.data?.stats?.total ?? 0) > 0)

const donutSegments = computed(() => {
  const stats = leadsData.data?.stats
  if (!stats || stats.total === 0) return []
  let cumulative = 0
  return stats.items.map((item: any, idx: number) => {
    const fraction = item.count / stats.total
    const dash     = fraction * CIRCUMFERENCE
    const gap      = CIRCUMFERENCE - dash
    const offset   = CIRCUMFERENCE * (1 - cumulative)
    cumulative += fraction
    // Always use our palette — ignore any server-supplied color
    return { ...item, dash, gap, offset, color: chartColor(item.status, idx) }
  })
})

const activityItems = [
  { key: 'feedback', label: 'Feedback', icon: LucideMessageSquare, color: '#2D71BF', bg: '#EFF6FF' },
  { key: 'whatsapp', label: 'WhatsApp', icon: LucideMessageCircle, color: '#D57C0C', bg: '#FFF7ED' },
]

const leadOverviewCards = computed(() => {
  const stats = leadsData.data?.stats?.items || []
  const getCount = (s: string) => stats.find((i: any) => i.status === s)?.count ?? 0
  return [
    { status: 'New',                  db_status: 'New',                  icon: LucideTarget,         color: '#2D71BF', bg: '#EFF6FF', count: getCount('New') },
    { status: 'Contacted',            db_status: 'Contacted',            icon: LucidePhoneForwarded, color: '#448DE1', bg: '#CBE3FF', count: getCount('Contacted') },
    { status: 'Nurture',              db_status: 'Nurture',              icon: LucideActivity,       color: '#1A579D', bg: '#A7D0FF', count: getCount('Nurture') },
    { status: 'Qualified',            db_status: 'Qualified',            icon: LucideCheckCircle,    color: '#D57C0C', bg: '#FFDEB6', count: getCount('Qualified') },
    { status: 'Unqualified',          db_status: 'Unqualified',          icon: LucideThumbsDown,     color: '#737373', bg: '#F5F5F5', count: getCount('Unqualified') },
    { status: 'Junk',                 db_status: 'Junk',                 icon: LucideXCircle,        color: '#EF4444', bg: '#FEF2F2', count: getCount('Junk') },
    { status: 'Meeting',              db_status: 'Meeting',              icon: LucideCalendarCheck,  color: '#F7961D', bg: '#FFF7ED', count: getCount('Meeting') },
    { status: 'Follow Up To Meeting', db_status: 'Follow Up To Meeting', icon: LucideClock,          color: '#B36300', bg: '#FFFBEB', count: getCount('Follow Up To Meeting') },
    { status: 'Reserved',             db_status: 'Reserved',             icon: LucideBookmark,       color: '#0C407B', bg: '#CBE3FF', count: getCount('Reserved') },
  ]
})


const lostReasonChartData = computed(() => {
  const rs: any[] = leadsData.data?.lost_reasons || []
  if (!rs.length) return []
  const maxCount = Math.max(...rs.map((r: any) => r.count ?? 0), 1)
  return rs.map((r: any, i: number) => ({
    reason:    r.reason,
    count:     r.count ?? 0,
    color:     chartColor(r.reason, i),
    heightPct: Math.min(Math.max(((r.count ?? 0) / maxCount) * 85, (r.count ?? 0) > 0 ? 12 : 4), 85),
  }))
})

const leadSourcesChartData = computed(() => {
  const sources: any[] = leadsData.data?.source_chart || []
  if (!sources.length) return []
  const maxTotal = Math.max(...sources.map((s: any) => s.total ?? 0), 1)
  return sources.map((s: any) => ({
    source:      s.source,
    total:       s.total ?? 0,
    won:         s.won   ?? 0,
    totalHeight: (s.total ?? 0) > 0 ? Math.min(Math.max(((s.total ?? 0) / maxTotal) * 80, 10), 90) : 5,
    wonHeight:   (s.won   ?? 0) > 0 ? Math.min(Math.max(((s.won   ?? 0) / maxTotal) * 80,  8), 80) : 3,
  }))
})

// ── Tasks breakdown panels (DRY) ───────────────────────────────────────────────
const taskBreakdownPanels = computed(() => [
  { title: 'By Status',    key: 'status',   items: tasksData.data?.status_breakdown   || [] },
  { title: 'By Task Type', key: 'type',     items: tasksData.data?.type_breakdown     || [] },
  { title: 'By Priority',  key: 'priority', items: tasksData.data?.priority_breakdown || [] },
])

// ── Inventory computed ─────────────────────────────────────────────────────────
const inventoryPerformanceData = computed(() => inventoryData.data?.performance || [])

const inventoryProfitsData = computed(() => inventoryData.data?.profits || [
  { type: 'Expected',   value: 0, color: '#448DE1' },
  { type: 'Realized',   value: 0, color: '#F7961D' },
  { type: 'Difference', value: 0, color: '#2D71BF' },
])

const inventoryReservationsData = computed(() => inventoryData.data?.reservations || [
  { type: 'Current',   value: 0, color: '#2D71BF' },
  { type: 'Completed', value: 0, color: '#D57C0C' },
  { type: 'Cancelled', value: 0, color: '#EF4444' },
])

const profitMax = computed(() => Math.max(...inventoryProfitsData.value.map((d: any) => d.value || 0), 1))
const reservMax = computed(() => Math.max(...inventoryReservationsData.value.map((d: any) => d.value || 0), 1))

const profitBarHeight      = (v: number) => v > 0 ? Math.max((v / profitMax.value) * 80, 8) : 4
const reservationBarHeight = (v: number) => v > 0 ? Math.max((v / reservMax.value) * 80, 8) : 4

// ── Utilities ──────────────────────────────────────────────────────────────────
function buildLeadQuery(extra: Record<string, string> = {}) {
  const q: Record<string, string> = { ...extra }
  if (filters.user) q.user = filters.user
  return q
}

usePageMeta(() => ({ title: __('CRM Dashboard') }))
</script>
