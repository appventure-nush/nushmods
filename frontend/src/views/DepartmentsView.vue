<template>
  <v-container>
    <h1 class="text-center">Departments</h1>
    <v-row>
      <v-col cols="12" md="6" lg="4" xl="3" v-for="department in departments" :key="department.code">
        <v-card @click="select(department.code)">
          <v-card-title>{{ department.name }}</v-card-title>
          <v-card-subtitle>{{ department.code }}</v-card-subtitle>
        </v-card>
      </v-col>
    </v-row>
    <v-snackbar v-model="snackbar">
      Invalid Department
      <template v-slot:action="{ attrs }">
        <v-btn
          color="accent"
          text
          v-bind="attrs"
          @click="snackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
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
    snackbar: false,
  }),
  methods: {
    select(code: string) {
      this.$router.push({
        name: "departmentDetails",
        params: {
          code: code,
        },
      });
    },
  },
  async mounted() {
    this.departments = await getDepartments();
    if (this.$route.params.invalid !== undefined) {
      this.snackbar = true;
    }
  },
});
</script>
