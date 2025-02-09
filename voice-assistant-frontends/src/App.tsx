import React, { useState, useRef } from "react";
import { FaMicrophone, FaStop } from "react-icons/fa";
import { Mic, StopCircle, Volume2, Search, Calendar, HelpCircle } from 'lucide-react';
import './App.css';


const VoiceAssistant: React.FC = () => {
  const [responseAudio, setResponseAudio] = useState<string | null>(null);
  const [recording, setRecording] = useState<boolean>(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.wav");

        try {
          // 🔹 Send voice command to Flask backend
          const response = await fetch("http://localhost:5000/process_audio", {
            method: "POST",
            body: formData
          });

          if (!response.ok) {
            throw new Error("Failed to fetch response");
          }

          // 🔹 Get the audio response as a blob
          const audioResponseBlob = await response.blob();
          const audioUrl = URL.createObjectURL(audioResponseBlob);
          setResponseAudio(audioUrl);

        } catch (error) {
          console.error("Error sending audio:", error);
        }
      };

      mediaRecorder.start();
      setRecording(true);
    } catch (error) {
      console.error("Microphone access denied:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  return (
    <div className="voice-assistant">
<div className="assistant-container">
  <div className="assistant-header">
    <h1>Voice Assistant</h1>
  </div>
  <div className="assistant-body">
    <div className="response-area">
     {/* 🎵 Play the assistant's response */}
     <p>How can I help you today?</p>
    </div>
    <div className="transcript-area">
      <p>{transcript || "Your voice input will appear here..."}</p>
      {responseAudio && (
        <div className="mt-6">
          <audio ref={audioRef} controls src={responseAudio} autoPlay />
          <Volume2 className="response-icon" />
        </div>
      )}
    </div>
    <div className="feature-list">
      <div className="feature">
        <Search /> Web Search
      </div>
      <div className="feature">
        <Calendar /> Set Reminders
      </div>
      <div className="feature">
        <HelpCircle /> Answer Questions
      </div>
    </div>
  </div>
  <div className="assistant-footer">
  <button
          onClick={recording ? stopRecording : startRecording}
          className={`voice-button ${recording ? "bg-red-500 hover:bg-red-600" : "bg-green-500 hover:bg-green-600"}`}
        >
          {recording ? <FaStop size={32} /> : <FaMicrophone size={32} />}
      
        </button>
    <p>{isListening ? 'Listening...' : 'Press to speak'}</p>
  </div>
</div>
</div>
);
};

export default VoiceAssistant;
