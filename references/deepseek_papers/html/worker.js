export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    // Strip the /work/deepseek/ prefix for assets lookup
    const cleanPath = url.pathname.replace(/^\/work\/deepseek/, '') || '/';
    const newUrl = new URL(cleanPath, 'https://placeholder');
    const newRequest = new Request(newUrl, request);
    try {
      return await env.ASSETS.fetch(newRequest);
    } catch (e) {
      return new Response('Not Found: ' + cleanPath, { status: 404 });
    }
  }
};
