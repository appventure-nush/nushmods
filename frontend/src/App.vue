<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <router-link style="text-decoration: none; color: inherit" to="/">
        <h2>NUSHMods</h2>
      </router-link>
      <v-spacer />
      <v-switch color="white" hide-details inset v-model="$vuetify.theme.dark">
        <template v-slot:prepend>
          <v-icon class="me-1" v-if="$vuetify.theme.dark">mdi-weather-night</v-icon>
          <v-icon class="me-1" v-else>mdi-white-balance-sunny</v-icon>
        </template>
      </v-switch>
      <v-menu
        open-on-hover
        offset-y
      >
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            text
            v-bind="attrs"
            v-on="on"
          >
            Tools
          </v-btn>
        </template>
        <v-list>
          <v-list-item to="/planner">
            Planner
          </v-list-item>
        </v-list>
      </v-menu>
      <v-btn text to="/departments">
        Departments
      </v-btn>
      <v-btn text to="/modules">
        Modules
      </v-btn>
      <v-btn text to="/about">
        About
      </v-btn>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script lang="ts">
import Vue from "vue";

export default Vue.extend({
  name: "App",

  data: () => ({
    //
  }),
});
</script>
