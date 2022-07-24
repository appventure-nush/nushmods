<template>
  <v-container>
    <h1 class="text-center">Modules</h1>
    <v-row>
      <v-col cols="6">
        <v-switch v-model="showDescription" label="Show Description" />
        <v-data-table
          class="elevation-1 rounded-lg"
          :headers="filteredModuleHeaders"
          :items="filteredModules"
          @click:row="select"
        />
      </v-col>
      <v-col cols="5">
        <module-details
          class="elevation-2 rounded-lg pa-5 ma-5 me-0"
          v-if="selectedModule"
          :module="selectedModule"
          @close="close"
        />
        <module-filter v-else v-model="filter.params" @clear="clearFilter" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import Vue from "vue";
import { Module, Filter } from "@/types/module";
import { getModules } from "@/api/api";
import ModuleDetails from "../components/ModuleDetails.vue";
import ModuleFilter from "../components/ModuleFilter.vue";

export default Vue.extend({
  name: "ModulesView",
  components: {
    ModuleDetails,
    ModuleFilter,
  },
  data: () => ({
    showDescription: false,
    moduleHeaders: [
      { text: "Module Code", value: "code" },
      { text: "Title", value: "title" },
      { text: "Description", value: "description" },
      { text: "MCs", value: "mcs" },
      { text: "Hours", value: "hours" },
    ],
    modules: [] as Module[],
    selectedModule: null as Module | null,
    filter: new Filter(),
  }),
  computed: {
    filteredModuleHeaders() {
      return this.showDescription
        ? this.moduleHeaders
        : this.moduleHeaders.filter((header) => header.value !== "description");
    },
    filteredModules() {
      return this.modules.filter((module) => this.filter.check(module));
    },
  },
  methods: {
    select(module: Module) {
      this.selectedModule = this.selectedModule === module ? null : module;
    },
    close() {
      this.selectedModule = null;
    },
    clearFilter() {
      this.filter = new Filter();
    },
  },
  async mounted() {
    this.modules = await getModules();
  },
});
</script>
