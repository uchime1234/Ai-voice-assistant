declare module 'react-mic' {
    import * as React from 'react';
  
    export interface ReactMicProps {
      record: boolean;
      onStop: (recordedData: ReactMicStopEvent) => void;
      mimeType?: string;
      strokeColor?: string;
      backgroundColor?: string;
    }
  
    export interface ReactMicStopEvent {
      blob: Blob;
      startTime: number;
      stopTime: number;
      option: any;
    }
  
    declare const ReactMic: React.ComponentType<ReactMicProps>;
    export default ReactMic;
  }