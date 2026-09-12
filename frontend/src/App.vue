<script setup>
import { computed, ref } from 'vue';

const API_BASE_URL = 'http://127.0.0.1:8000';

const hotelName = ref('');
const matches = ref([]);
const message = ref('Enter a hotel name and select Search.');
const isLoading = ref(false);

const tableRows = computed(() =>
  matches.value.flatMap((hotel) => {
    if (hotel.available_stays.length === 0) {
      return [{ hotel, stay: null }];
    }

    return hotel.available_stays.map((stay) => ({ hotel, stay }));
  })
);

async function searchHotels() {
  const query = hotelName.value.trim();
  matches.value = [];

  if (!query) {
    message.value = 'Enter a hotel name before searching.';
    return;
  }

  isLoading.value = true;
  message.value = 'Searching...';

  try {
    const response = await fetch(`${API_BASE_URL}/api/search?hotel_name=${encodeURIComponent(query)}`);
    if (!response.ok) {
      throw new Error('The search service could not complete the request.');
    }

    const data = await response.json();
    matches.value = data.matches;
    message.value = data.matches.length === 0
      ? `No hotels and available stays found for “${query}”.`
      : `${data.matches.length} matching hotel${data.matches.length === 1 ? '' : 's'} found.`;
  } catch (error) {
    message.value = error.message;
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <main>
    <h1>Hotel search</h1>

    <form @submit.prevent="searchHotels">
      <label for="hotel-name">Hotel name</label>
      <input id="hotel-name" v-model="hotelName" type="search">
      <button type="submit" :disabled="isLoading">Search</button>
    </form>

    <p aria-live="polite">{{ message }}</p>

    <table v-if="tableRows.length > 0">
      <thead>
        <tr>
          <th scope="col">Hotel ID</th>
          <th scope="col">Hotel name</th>
          <th scope="col">City</th>
          <th scope="col">State</th>
          <th scope="col">Nightly rate (USD)</th>
          <th scope="col">Trip ID</th>
          <th scope="col">Available stay</th>
          <th scope="col">Check-in</th>
          <th scope="col">Check-out</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in tableRows" :key="`${row.hotel.hotel_id}-${row.stay?.trip_id ?? 'none'}`">
          <td>{{ row.hotel.hotel_id }}</td>
          <td>{{ row.hotel.hotel_name }}</td>
          <td>{{ row.hotel.city }}</td>
          <td>{{ row.hotel.state }}</td>
          <td>${{ Number(row.hotel.nightly_rate_usd).toFixed(2) }}</td>
          <td>{{ row.stay?.trip_id ?? '—' }}</td>
          <td>{{ row.stay?.trip_name ?? 'No available stays' }}</td>
          <td>{{ row.stay?.check_in ?? '—' }}</td>
          <td>{{ row.stay?.check_out ?? '—' }}</td>
        </tr>
      </tbody>
    </table>
  </main>
</template>
