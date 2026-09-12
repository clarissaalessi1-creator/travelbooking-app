const hotels = [
  { id: 'H001', name: 'Liberty Lane Inn', city: 'Philadelphia', stars: 4, nightlyRate: 189.0 },
  { id: 'H002', name: 'Harbor Square Inn', city: 'Boston', stars: 4, nightlyRate: 205.0 },
  { id: 'H003', name: 'Valley Trail Inn', city: 'San Diego', stars: 3, nightlyRate: 175.0 }
];

const searchForm = document.querySelector('#hotel-search-form');
const hotelNameInput = document.querySelector('#hotel-name');
const resultCount = document.querySelector('#result-count');
const hotelResults = document.querySelector('#hotel-results');

function createCell(value) {
  const cell = document.createElement('td');
  cell.textContent = value;
  return cell;
}

function renderHotels() {
  const searchTerm = hotelNameInput.value.trim().toLowerCase();
  const matchingHotels = hotels.filter((hotel) => hotel.name.toLowerCase().includes(searchTerm));

  resultCount.textContent = `${matchingHotels.length} hotel${matchingHotels.length === 1 ? '' : 's'} found`;
  hotelResults.replaceChildren();

  matchingHotels.forEach((hotel) => {
    const row = document.createElement('tr');
    row.append(
      createCell(hotel.id),
      createCell(hotel.name),
      createCell(hotel.city),
      createCell(`${hotel.stars} stars`),
      createCell(`$${hotel.nightlyRate.toFixed(2)}`)
    );
    hotelResults.append(row);
  });
}

searchForm.addEventListener('submit', (event) => {
  event.preventDefault();
  renderHotels();
});

renderHotels();
