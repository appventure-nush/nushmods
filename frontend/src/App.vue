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
      <v-btn text>
        <router-link style="text-decoration: none; color: inherit" to="/modules">
          Modules
        </router-link>
      </v-btn>
      <v-btn text>
        <router-link style="text-decoration: none; color: inherit" to="/about">
          About
        </router-link>
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
