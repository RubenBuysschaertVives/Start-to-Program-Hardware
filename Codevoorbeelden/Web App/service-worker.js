self.addEventListener('install', (event) => {
    console.log('Service worker installed: ', event);   
});

self.addEventListener('activate', (event) => {
    console.log('Service worker activated: ', event);    
});

self.addEventListener('fetch', (event) => {
   console.log('Service worker fetched: ', event);
});