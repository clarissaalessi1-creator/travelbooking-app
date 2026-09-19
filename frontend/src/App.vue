<script setup>
import { computed, onMounted, ref } from 'vue';

const API_BASE_URL = 'http://127.0.0.1:8000';

const hotelName = ref('');
const matches = ref([]);
const searchMessage = ref('Enter a hotel name and select Search.');
const isSearching = ref(false);

const users = ref([]);
const selectedUserId = ref('');
const travelerMessage = ref('Loading demo travelers...');

const bookings = ref([]);
const historyMessage = ref('Loading booking history...');
const bookingMessage = ref('Select a traveler, then search for a hotel to book a stay.');
const isBooking = ref(false);
const isHistoryLoading = ref(false);

const selectedTraveler = computed(() =>
  users.value.find((user) => user.user_id === selectedUserId.value)
);

const tableRows = computed(() =>
  matches.value.flatMap((hotel) => {
    if (hotel.available_stays.length === 0) {
      return [{ hotel, stay: null }];
    }

    return hotel.available_stays.map((stay) => ({ hotel, stay }));
  })
);

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || 'The service could not complete the request.');
  }

  return data;
}

async function loadUsers() {
  try {
    const data = await apiRequest('/api/users');
    users.value = data.users;
    if (!selectedUserId.value && users.value.length > 0) {
      selectedUserId.value = users.value[0].user_id;
    }
    travelerMessage.value = users.value.length === 0
      ? 'No travelers are available.'
      : 'Choose a traveler for new bookings.';
  } catch (error) {
    travelerMessage.value = error.message;
  }
}

async function refreshBookingHistory() {
  isHistoryLoading.value = true;
  historyMessage.value = 'Loading booking history...';

  try {
    const data = await apiRequest('/api/bookings');
    bookings.value = data.bookings;
    historyMessage.value = bookings.value.length === 0
      ? 'No bookings found.'
      : `${bookings.value.length} booking${bookings.value.length === 1 ? '' : 's'} in history.`;
  } catch (error) {
    historyMessage.value = error.message;
  } finally {
    isHistoryLoading.value = false;
  }
}

async function searchHotels() {
  const query = hotelName.value.trim();
  matches.value = [];

  if (!query) {
    searchMessage.value = 'Enter a hotel name before searching.';
    return;
  }

  isSearching.value = true;
  searchMessage.value = 'Searching...';

  try {
    const data = await apiRequest(`/api/search?hotel_name=${encodeURIComponent(query)}`);
    matches.value = data.matches;
    searchMessage.value = data.matches.length === 0
      ? `No hotels and available stays found for “${query}”.`
      : `${data.matches.length} matching hotel${data.matches.length === 1 ? '' : 's'} found.`;
  } catch (error) {
    searchMessage.value = error.message;
  } finally {
    isSearching.value = false;
  }
}

async function createBooking(tripId) {
  if (!selectedUserId.value) {
    bookingMessage.value = 'Select a traveler before creating a booking.';
    return;
  }

  isBooking.value = true;
  bookingMessage.value = 'Creating booking...';

  try {
    const booking = await apiRequest('/api/bookings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: selectedUserId.value, trip_id: tripId }),
    });
    bookingMessage.value = `Booking ${booking.booking_id} created for ${booking.display_name}.`;
    await refreshBookingHistory();
  } catch (error) {
    bookingMessage.value = error.message;
  } finally {
    isBooking.value = false;
  }
}

async function cancelBooking(bookingId) {
  isBooking.value = true;
  bookingMessage.value = `Cancelling ${bookingId}...`;

  try {
    const booking = await apiRequest(`/api/bookings/${bookingId}/cancel`, { method: 'PATCH' });
    bookingMessage.value = `Booking ${booking.booking_id} is now ${booking.status}.`;
    await refreshBookingHistory();
  } catch (error) {
    bookingMessage.value = error.message;
  } finally {
    isBooking.value = false;
  }
}

async function deleteBooking(bookingId) {
  isBooking.value = true;
  bookingMessage.value = `Deleting test booking ${bookingId}...`;

  try {
    const result = await apiRequest(`/api/bookings/${bookingId}`, { method: 'DELETE' });
    bookingMessage.value = result.message;
    await refreshBookingHistory();
  } catch (error) {
    bookingMessage.value = error.message;
  } finally {
    isBooking.value = false;
  }
}

onMounted(() => {
  loadUsers();
  refreshBookingHistory();
});
</script>

<template>
  <main>
    <h1>Hotel search and bookings</h1>

    <section aria-labelledby="traveler-heading">
      <h2 id="traveler-heading">Traveler</h2>
      <label for="traveler">Book as</label>
      <select id="traveler" v-model="selectedUserId" :disabled="users.length === 0">
        <option v-for="user in users" :key="user.user_id" :value="user.user_id">
          {{ user.display_name }} ({{ user.user_id }})
        </option>
      </select>
      <p aria-live="polite">{{ travelerMessage }}</p>
      <p v-if="selectedTraveler">Selected traveler: {{ selectedTraveler.display_name }}</p>
    </section>

    <section aria-labelledby="search-heading">
      <h2 id="search-heading">Hotel search</h2>
      <form @submit.prevent="searchHotels">
        <label for="hotel-name">Hotel name</label>
        <input id="hotel-name" v-model="hotelName" type="search">
        <button type="submit" :disabled="isSearching">Search</button>
      </form>

      <p aria-live="polite">{{ searchMessage }}</p>

      <div v-if="tableRows.length > 0" class="table-wrap">
        <table>
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
              <th scope="col">Booking</th>
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
              <td>
                <button
                  v-if="row.stay"
                  type="button"
                  :disabled="isBooking || !selectedUserId"
                  @click="createBooking(row.stay.trip_id)"
                >
                  Book
                </button>
                <span v-else>—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section aria-labelledby="history-heading">
      <h2 id="history-heading">Booking history</h2>
      <button type="button" :disabled="isHistoryLoading" @click="refreshBookingHistory">Refresh history</button>
      <p aria-live="polite">{{ bookingMessage }}</p>
      <p aria-live="polite">{{ historyMessage }}</p>

      <div v-if="bookings.length > 0" class="table-wrap">
        <table>
          <thead>
            <tr>
              <th scope="col">Booking ID</th>
              <th scope="col">Traveler</th>
              <th scope="col">Hotel</th>
              <th scope="col">Trip</th>
              <th scope="col">Check-in</th>
              <th scope="col">Check-out</th>
              <th scope="col">Booked on</th>
              <th scope="col">Status</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="booking in bookings" :key="booking.booking_id">
              <td>{{ booking.booking_id }}</td>
              <td>{{ booking.display_name }} ({{ booking.user_id }})</td>
              <td>{{ booking.hotel_name }}</td>
              <td>{{ booking.trip_name }} ({{ booking.trip_id }})</td>
              <td>{{ booking.check_in }}</td>
              <td>{{ booking.check_out }}</td>
              <td>{{ booking.booked_on }}</td>
              <td>{{ booking.status }}</td>
              <td>
                <button
                  v-if="booking.status === 'confirmed'"
                  type="button"
                  :disabled="isBooking"
                  @click="cancelBooking(booking.booking_id)"
                >
                  Cancel
                </button>
                <button
                  v-if="booking.can_delete"
                  type="button"
                  :disabled="isBooking"
                  @click="deleteBooking(booking.booking_id)"
                >
                  Delete (test)
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>
