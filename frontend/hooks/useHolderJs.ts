import { useEffect } from 'react';

export default function useHolderJs() {
  useEffect(() => {
    // Import Holder.js dynamically since it's a browser-only library
    import('holderjs').then(Holder => {
      // Run Holder.js to replace the placeholders
      Holder.default.run();
    });
  }, []);
}