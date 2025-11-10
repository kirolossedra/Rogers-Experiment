
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/wifi-module.h"
#include "ns3/mobility-module.h"
#include "ns3/applications-module.h"
#include "ns3/wifi-mac-header.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("WifiUdpUnicastAvgPerUserExample");

// Global variable to count UDP unicast bytes transmitted by the AP.
static uint64_t g_totalBytesTx = 0;

// Trace callback to record the size of each transmitted UDP unicast packet.
void
TxTrace (Ptr<const Packet> packet)
{
  // Create a copy so we can inspect its MAC header.
  Ptr<Packet> copy = packet->Copy();
  WifiMacHeader hdr;
  if (copy->PeekHeader (hdr))
    {
      // Count only data frames (ignore RTS, CTS, ACK, etc.)
      if (hdr.IsData ())
        {
          g_totalBytesTx += packet->GetSize ();
        }
    }
}

int main (int argc, char *argv[])
{
  // Simulation parameters
  uint32_t numStations = 20;
  double simulationTime = 10.0; // seconds
  uint16_t port = 9; // UDP port
  double txStartTime = 2.0; // when AP starts transmitting

  CommandLine cmd;
  cmd.AddValue ("numStations", "Number of station nodes", numStations);
  cmd.Parse (argc, argv);

  // Create node containers: one AP and numStations stations.
  NodeContainer staNodes;
  staNodes.Create (numStations);
  NodeContainer apNode;
  apNode.Create (1);

  // Configure WiFi (using 802.11g in infrastructure mode)
  WifiHelper wifi;
  wifi.SetStandard (WIFI_STANDARD_80211g);

  // Force RTS/CTS for packets above 500 bytes.
  wifi.SetRemoteStationManager ("ns3::ArfWifiManager", "RtsCtsThreshold", UintegerValue (500));

  YansWifiChannelHelper channel = YansWifiChannelHelper::Default ();
  YansWifiPhyHelper phy;
  phy.SetChannel (channel.Create ());

  // Configure MAC layer and set a common SSID.
  WifiMacHelper mac;
  Ssid ssid = Ssid ("ns-3-unicast");

  // Install WiFi devices on the station nodes.
  mac.SetType ("ns3::StaWifiMac",
               "Ssid", SsidValue (ssid),
               "ActiveProbing", BooleanValue (false));
  NetDeviceContainer staDevices = wifi.Install (phy, mac, staNodes);

  // Install WiFi device on the AP.
  mac.SetType ("ns3::ApWifiMac",
               "Ssid", SsidValue (ssid));
  NetDeviceContainer apDevice = wifi.Install (phy, mac, apNode);

  // Attach trace callback to the AP's PHY layer.
  Ptr<WifiNetDevice> apWifiDevice = apDevice.Get (0)->GetObject<WifiNetDevice> ();
  apWifiDevice->GetPhy ()->TraceConnectWithoutContext ("PhyTxEnd", MakeCallback (&TxTrace));

  // Enable PCAP tracing to capture packets (including RTS/CTS) for Wireshark.
  phy.EnablePcap ("ap-unicast-trace", apDevice.Get (0));

  // Set up mobility: place stations in a grid and the AP at a fixed position.
  MobilityHelper mobility;
  mobility.SetPositionAllocator ("ns3::GridPositionAllocator",
                                 "MinX", DoubleValue (0.0),
                                 "MinY", DoubleValue (0.0),
                                 "DeltaX", DoubleValue (10.0),
                                 "DeltaY", DoubleValue (10.0),
                                 "GridWidth", UintegerValue (5));
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (staNodes);
  mobility.Install (apNode);

  // Install the Internet stack on all nodes.
  InternetStackHelper stack;
  stack.Install (staNodes);
  stack.Install (apNode);

  // Assign IP addresses.
  Ipv4AddressHelper address;
  address.SetBase ("10.1.4.0", "255.255.255.0");
  NetDeviceContainer allDevices;
  allDevices.Add (staDevices);
  allDevices.Add (apDevice);
  Ipv4InterfaceContainer interfaces = address.Assign (allDevices);

  // Install a UDP server on each station to receive unicast traffic.
  UdpServerHelper udpServer (port);
  ApplicationContainer serverApps;
  for (uint32_t i = 0; i < staNodes.GetN (); ++i)
    {
      serverApps.Add (udpServer.Install (staNodes.Get (i)));
    }
  serverApps.Start (Seconds (1.0));
  serverApps.Stop (Seconds (simulationTime + 1));

  // Install a UDP client on the AP for each station.
  for (uint32_t i = 0; i < staNodes.GetN (); ++i)
    {
      Ipv4Address dstAddress = interfaces.GetAddress (i); // station's IP address
      UdpClientHelper udpClient (dstAddress, port);
      udpClient.SetAttribute ("MaxPackets", UintegerValue (100));
      udpClient.SetAttribute ("Interval", TimeValue (Seconds (0.1)));
      udpClient.SetAttribute ("PacketSize", UintegerValue (1024));

      ApplicationContainer clientApps = udpClient.Install (apNode.Get (0));
      clientApps.Start (Seconds (txStartTime));
      clientApps.Stop (Seconds (simulationTime));
    }

  // Run the simulation.
  Simulator::Stop (Seconds (simulationTime + 1));
  Simulator::Run ();
  Simulator::Destroy ();

  // Calculate the aggregate throughput (in Mbps) over the transmission period.
  double txDuration = simulationTime - txStartTime;
  double aggregateThroughput = (g_totalBytesTx * 8.0) / (txDuration * 1e6); // in Mbps

  // Average throughput per user is the aggregate divided by the number of stations.
  double avgThroughputPerUser = aggregateThroughput / numStations;

  std::cout << "Total transmitted UDP unicast bytes from AP: " << g_totalBytesTx << std::endl;
  std::cout << "Aggregate UDP unicast throughput of the AP: " << aggregateThroughput << " Mbps" << std::endl;
  std::cout << "Average UDP unicast throughput per user: " << avgThroughputPerUser << " Mbps" << std::endl;

  return 0;
}
