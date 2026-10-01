<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

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

const nearbyZipCode = ref('');
const nearbyHotels = ref([]);
const nearbyOutcome = ref('idle');
const nearbyMessage = ref('Enter a five-digit U.S. ZIP code to find nearby hotel-provider results.');
const nearbyInventoryNotice = ref('');
const isNearbySearching = ref(false);
const selectedPlaceId = ref('');
const nearbyMapContainer = ref(null);

const DEFAULT_MAP_CENTER = [39.8283, -98.5795];
let nearbyMap;
let nearbyMarkerLayer;
let nearbyRadiusCircle;
const nearbyMarkers = new Map();
const nearbyHotelRows = new Map();

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

function buildNearbyPopup(hotel) {
  const popup = document.createElement('div');
  const title = document.createElement('strong');
  title.textContent = nearbyHotelDisplayName(hotel);
  popup.append(title);

  if (hotel.address) {
    const address = document.createElement('div');
    address.textContent = hotel.address;
    popup.append(address);
  }

  return popup;
}

function nearbyHotelDisplayName(hotel) {
  return hotel.hotel_name || 'Hotel name unavailable from provider.';
}

function nearbyMarkerStyle(placeId) {
  const isSelected = placeId === selectedPlaceId.value;
  return {
    radius: isSelected ? 11 : 8,
    color: isSelected ? '#8a2d1e' : '#1d65a6',
    fillColor: isSelected ? '#d35d3d' : '#3f88c5',
    fillOpacity: 1,
    weight: isSelected ? 3 : 2,
  };
}

function initializeNearbyMap() {
  if (!nearbyMapContainer.value || nearbyMap) {
    return;
  }

  nearbyMap = L.map(nearbyMapContainer.value).setView(DEFAULT_MAP_CENTER, 4);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
  }).addTo(nearbyMap);
  nearbyMarkerLayer = L.layerGroup().addTo(nearbyMap);
}

function clearNearbyMap(resetView = true) {
  nearbyMarkerLayer?.clearLayers();
  nearbyMarkers.clear();
  if (nearbyRadiusCircle) {
    nearbyRadiusCircle.remove();
    nearbyRadiusCircle = undefined;
  }
  if (resetView) {
    nearbyMap?.setView(DEFAULT_MAP_CENTER, 4);
  }
}

function updateNearbyMarkerStyles() {
  for (const [placeId, marker] of nearbyMarkers) {
    marker.setStyle(nearbyMarkerStyle(placeId));
  }
}

function setNearbyHotelRow(element, placeId) {
  if (element) {
    nearbyHotelRows.set(placeId, element);
  } else {
    nearbyHotelRows.delete(placeId);
  }
}

function selectNearbyHotel(placeId, focusList = false) {
  const hotel = nearbyHotels.value.find((candidate) => candidate.provider_place_id === placeId);
  const marker = nearbyMarkers.get(placeId);
  if (!hotel || !marker) {
    return;
  }

  selectedPlaceId.value = placeId;
  updateNearbyMarkerStyles();
  marker.openPopup();
  nearbyMap?.panTo(marker.getLatLng());

  if (focusList) {
    nextTick(() => {
      const row = nearbyHotelRows.get(placeId);
      row?.scrollIntoView({ block: 'nearest' });
      row?.focus({ preventScroll: true });
    });
  }
}

function renderNearbyMap(center, hotels) {
  initializeNearbyMap();
  if (!nearbyMap || !nearbyMarkerLayer) {
    return;
  }

  clearNearbyMap(false);
  const location = [center.latitude, center.longitude];
  nearbyRadiusCircle = L.circle(location, {
    radius: 5000,
    color: '#1d65a6',
    fillColor: '#3f88c5',
    fillOpacity: 0.08,
    weight: 2,
  }).addTo(nearbyMap);

  for (const hotel of hotels) {
    const marker = L.circleMarker(
      [hotel.latitude, hotel.longitude],
      nearbyMarkerStyle(hotel.provider_place_id),
    ).addTo(nearbyMarkerLayer);
    marker.bindPopup(buildNearbyPopup(hotel));
    marker.on('click', () => selectNearbyHotel(hotel.provider_place_id, true));
    nearbyMarkers.set(hotel.provider_place_id, marker);
  }

  nearbyMap.fitBounds(nearbyRadiusCircle.getBounds(), { padding: [24, 24] });
  window.setTimeout(() => nearbyMap.invalidateSize(), 0);
}

async function nearbyHotelRequest(zipCode) {
  const response = await fetch(`${API_BASE_URL}/api/nearby-hotels?zip_code=${encodeURIComponent(zipCode)}`);
  const data = await response.json().catch(() => ({}));
  if (response.ok) {
    return data;
  }
  if (data.detail && typeof data.detail === 'object') {
    return data.detail;
  }
  return {
    outcome: 'api_failure',
    message: 'Hotel map search is temporarily unavailable. Please try again later.',
  };
}

async function searchNearbyHotels() {
  const zipCode = nearbyZipCode.value.trim();
  nearbyHotels.value = [];
  selectedPlaceId.value = '';
  nearbyInventoryNotice.value = '';
  clearNearbyMap();

  if (!/^\d{5}$/.test(zipCode)) {
    nearbyOutcome.value = 'invalid_zip';
    nearbyMessage.value = 'Enter exactly five digits for a U.S. ZIP code.';
    return;
  }

  isNearbySearching.value = true;
  nearbyOutcome.value = 'loading';
  nearbyMessage.value = `Searching for hotel-provider results near ${zipCode}…`;

  try {
    const data = await nearbyHotelRequest(zipCode);
    nearbyOutcome.value = data.outcome || 'api_failure';
    nearbyMessage.value = data.message || 'Hotel map search is temporarily unavailable. Please try again later.';
    nearbyInventoryNotice.value = data.inventory_notice || '';

    if (data.outcome === 'success' || data.outcome === 'no_results') {
      nearbyHotels.value = Array.isArray(data.hotels) ? data.hotels : [];
      await nextTick();
      renderNearbyMap(data.center, nearbyHotels.value);
      if (data.outcome === 'success' && nearbyHotels.value.length > 0) {
        selectNearbyHotel(nearbyHotels.value[0].provider_place_id);
      }
    }
  } catch (_) {
    nearbyOutcome.value = 'failed_request';
    nearbyMessage.value = 'Hotel map search could not reach the local service. Please try again later.';
  } finally {
    isNearbySearching.value = false;
  }
}

onMounted(() => {
  initializeNearbyMap();
  loadUsers();
  refreshBookingHistory();
});

onBeforeUnmount(() => {
  nearbyMap?.remove();
  nearbyMap = undefined;
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

    <section aria-labelledby="nearby-hotels-heading">
      <h2 id="nearby-hotels-heading">Nearby hotel map</h2>
      <form class="nearby-form" novalidate @submit.prevent="searchNearbyHotels">
        <label for="nearby-zip-code">Five-digit U.S. ZIP code</label>
        <input
          id="nearby-zip-code"
          v-model="nearbyZipCode"
          type="text"
          inputmode="numeric"
          autocomplete="postal-code"
          maxlength="5"
          pattern="[0-9]{5}"
          aria-describedby="nearby-search-help nearby-search-status"
        >
        <button type="submit" :disabled="isNearbySearching">Search nearby hotels</button>
      </form>
      <p id="nearby-search-help">Searches Geoapify hotel-provider results within 5 km of the ZIP-code location.</p>
      <p id="nearby-search-status" aria-live="polite">{{ nearbyMessage }}</p>

      <div class="nearby-layout">
        <div class="nearby-list-panel" aria-label="Nearby hotel results">
          <p v-if="nearbyHotels.length === 0 && nearbyOutcome === 'no_results'">No hotel list is available for this search.</p>
          <ul v-if="nearbyHotels.length > 0" class="nearby-hotel-list">
            <li v-for="hotel in nearbyHotels" :key="hotel.provider_place_id">
              <button
                :ref="(element) => setNearbyHotelRow(element, hotel.provider_place_id)"
                class="nearby-hotel-button"
                :class="{ selected: hotel.provider_place_id === selectedPlaceId }"
                type="button"
                :aria-pressed="hotel.provider_place_id === selectedPlaceId"
                @click="selectNearbyHotel(hotel.provider_place_id)"
              >
                <span class="nearby-hotel-name">{{ nearbyHotelDisplayName(hotel) }}</span>
                <span v-if="hotel.provider_place_id === selectedPlaceId" class="selected-label">Selected</span>
                <span>{{ hotel.address || 'Address unavailable from provider.' }}</span>
              </button>
            </li>
          </ul>
        </div>

        <div class="nearby-map-panel">
          <div id="nearby-hotels-map" ref="nearbyMapContainer" aria-label="Map of nearby hotel-provider results"></div>
        </div>
      </div>
      <p v-if="nearbyInventoryNotice" class="inventory-notice">{{ nearbyInventoryNotice }}</p>
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
