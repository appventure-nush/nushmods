<template>
  <v-container>
    <v-row>
      <v-col>
        <h1>{{ module.code }}</h1>
      </v-col>
      <v-spacer />
      <v-col cols="1">
        <v-icon @click="close">mdi-close</v-icon>
      </v-col>
    </v-row>
    <h3>{{ module.title }}</h3>
    <v-btn @click="direct">{{ module.department }}</v-btn>
    <br />
    <br />
    <p>{{ module.description }}</p>
  </v-container>
</template>

<script lang="ts">
import Vue, { PropType } from "vue";
import { Module } from "@/types/module";

export default Vue.extend({
  name: "ModuleDetails",
  props: {
    module: {
      required: true,
      type: Object as PropType<Module>,
    },
  },
  data: () => ({}),
  methods: {
    direct() {
      this.$router.push({
        name: "departmentDetails",
        params: {
          code: this.module.department,
        },
      });
    },
    close() {
      this.$emit("close");
    },
  },
});
</script>
