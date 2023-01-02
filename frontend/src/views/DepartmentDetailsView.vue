<template>
  <v-container>
    <h1 class="text-center">Departments</h1>
    <v-row v-if="selectedDepartment">
      <v-col cols="6">
        <div>
          <h1>{{ selectedDepartment.name }}</h1>
          <br />
          <p>{{ selectedDepartment.description }}</p>
        </div>
        <v-btn @click="close">Close</v-btn>
      </v-col>
      <v-col cols="6">
        <h3>Module Listing</h3>
        <p>Work in Progress (timeline of modules taken)</p>
        <!-- <v-data-table
          class="elevation-1 rounded-lg"
          :headers="filteredDepartmentHeaders"
          :items="filteredDepartments"
          @click:row="select"
        /> -->
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import Vue from "vue";
import { Department } from "@/types/department";
import { getDepartments } from "@/api/api";

export default Vue.extend({
  name: "DepartmentsView",
  data: () => ({
    departments: [] as Department[],
    selectedDepartment: null as Department | null,
  }),
  methods: {
    close() {
      this.$router.push({ name: "departments" })
    },
  },
  async mounted() {
    this.departments = await getDepartments();
    const selectedCode = this.$route.params.code.toLowerCase();
    this.selectedDepartment = this.departments.find(dept => dept.code.toLowerCase() === selectedCode) ?? null;
    if (this.selectedDepartment === null) {
      this.$router.replace({
        name: "departments",
        params: {
          invalid: "",
        },
      });
    }
  },
});
</script>
