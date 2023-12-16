import HeroImage from '@/components/HeroImage'
import {GlobalStyles} from "@mui/material";
import SummarySection from "@/components/SummarySection";

export default function Home () {
  return (
    <>
      <GlobalStyles styles={{body: { backgroundColor: '#000010'} }} />
      <HeroImage />
      <SummarySection />
    </>
  )
}
