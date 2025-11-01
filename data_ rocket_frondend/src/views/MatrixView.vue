<template>
  <div class="p-6">
    <!-- Tech-Soft Pink header -->
    <header class="mb-4">
      <h1 class="text-2xl font-semibold text-[#FF66A1]">ALS Matrix • Folder → Forms</h1>
      <p class="text-sm text-gray-500">Upload ALS, expand Matrix (no “X”), and optionally compare with SSD.</p>
    </header>

    <section class="grid gap-4">
      <!-- Upload -->
      <div class="rounded-2xl p-4 shadow border border-pink-100">
        <label class="block text-sm font-medium mb-2 text-[#FF66A1]">ALS Excel (.xlsx)</label>
        <input type="file" accept=".xlsx" @change="onUpload" class="block" />
        <div class="mt-2">
          <textarea v-model="ssdJson" rows="5" placeholder='Optional SSD JSON: {"SVISIT01":["AE","CM"]}'
                    class="w-full rounded-xl border border-pink-200 p-3 text-sm outline-none focus:ring-2 focus:ring-pink-300"></textarea>
        </div>
        <button :disabled="loading"
                @click="submit"
                class="mt-3 px-4 py-2 rounded-xl shadow bg-[#FF66A1] text-white hover:opacity-90 disabled:opacity-50">
          {{ loading ? "Processing..." : "Extract Matrix" }}
        </button>
      </div>

      <!-- Result: Folder -> Forms -->
      <div v-if="result" class="rounded-2xl p-4 shadow border border-pink-100">
        <h2 class="text-xl font-semibold text-[#FF66A1] mb-3">Expanded Matrix</h2>
        <div class="grid gap-3">
          <div v-for="f in result.folders" :key="f.folderOID"
               class="rounded-xl border border-pink-200 p-3">
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium">{{ f.folderOID }}</div>
                <div class="text-xs text-gray-500" v-if="f.folderName">{{ f.folderName }}</div>
              </div>
              <span class="text-xs px-2 py-1 rounded-full bg-pink-50 border border-pink-200">
                {{ f.forms.length }} forms
              </span>
            </div>
            <ul class="mt-2 pl-4 list-disc">
              <li v-for="fm in f.forms" :key="fm.formOID" class="text-sm">
                <span class="font-mono">{{ fm.formOID }}</span>
                <span v-if="fm.formName" class="text-gray-500"> — {{ fm.formName }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Diff -->
      <div v-if="result && result.diff" class="rounded-2xl p-4 shadow border border-pink-100">
        <h2 class="text-xl font-semibold text-[#FF66A1] mb-3">SSD vs ALS Differences</h2>
        <div class="grid md:grid-cols-2 gap-4">
          <div class="rounded-xl border border-pink-200 p-3">
            <h3 class="font-medium text-pink-600 mb-2">Missing in DB (should exist)</h3>
            <div v-if="isEmpty(result.diff.missing_in_db)" class="text-sm text-gray-500">None</div>
            <div v-else class="space-y-2">
              <div v-for="(forms, foid) in result.diff.missing_in_db" :key="'miss-'+foid">
                <div class="font-mono text-sm">{{ foid }}</div>
                <div class="text-xs text-gray-600">{{ forms.join(", ") }}</div>
              </div>
            </div>
          </div>
          <div class="rounded-xl border border-pink-200 p-3">
            <h3 class="font-medium text-pink-600 mb-2">Extra in DB (not in SSD)</h3>
            <div v-if="isEmpty(result.diff.extra_in_db)" class="text-sm text-gray-500">None</div>
            <div v-else class="space-y-2">
              <div v-for="(forms, foid) in result.diff.extra_in_db" :key="'extra-'+foid">
                <div class="font-mono text-sm">{{ foid }}</div>
                <div class="text-xs text-gray-600">{{ forms.join(", ") }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"

const fileRef = ref<File | null>(null)
const ssdJson = ref<string>("")
const result = ref<any | null>(null)
const loading = ref(false)

function onUpload(e: Event) {
  const input = e.target as HTMLInputElement
  fileRef.value = input.files?.[0] ?? null
}

function isEmpty(obj: any) {
  return !obj || Object.keys(obj).length === 0
}

async function submit() {
  if (!fileRef.value) return
  loading.value = true
  try {
    const fd = new FormData()
    fd.append("als_file", fileRef.value)
    if (ssdJson.value.trim()) {
      // structured JSON string field supported by FastAPI if named param matches
      fd.append("ssd_folder_forms", new Blob([ssdJson.value], { type: "application/json" }))
    }
    const res = await fetch(import.meta.env.VITE_API_BASE + "/als/matrix", {
      method: "POST",
      body: fd
    })
    if (!res.ok) throw new Error(await res.text())
    result.value = await res.json()
  } catch (err) {
    alert("Upload/parse failed: " + err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Tech-Soft Pink accents */
</style>
