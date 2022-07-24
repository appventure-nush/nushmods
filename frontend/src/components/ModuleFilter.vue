<template>
  <v-container>
    <v-row>
      <v-col> </v-col>
      <v-spacer />
      <v-col cols="1">
        <v-icon @click="clearFilter">mdi-delete</v-icon>
      </v-col>
    </v-row>
    <h2>Filter</h2>
    <v-text-field
      label="Search"
      :value="value.search"
      @input="update('search', $event)"
    />
    <v-range-slider
      label="MCs"
      min="0"
      max="10"
      step="1"
      :tick-labels="[...Array(11).keys()].map((i) => i.toString())"
      :value="value.mcsRange"
      @input="update('mcsRange', $event)"
    ></v-range-slider>
    <v-range-slider
      label="Hours"
      min="0"
      max="5"
      step="0.5"
      :tick-labels="[...Array(11).keys()].map((i) => (i / 2).toString())"
      :value="value.hoursRange"
      @input="update('hoursRange', $event)"
    ></v-range-slider>
  </v-container>
</template>

<script lang="ts">
import Vue, { PropType } from "vue";
import { FilterParams } from "@/types/module";

export default Vue.extend({
  name: "ModuleFilter",
  props: {
    value: {
      required: true,
      type: Object as PropType<FilterParams>,
    },
  },
  methods: {
    update(key: string, value: unknown) {
      this.$emit("input", { ...this.value, [key]: value });
    },
    clearFilter() {
      this.$emit("clear");
    },
  },
});
</script>
