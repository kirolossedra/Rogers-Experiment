#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/wifi-module.h"
#include "ns3/mobility-module.h"
#include "ns3/applications-module.h"
#include "ns3/wifi-mac-header.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("WifiUdpBroadcastExample");

static uint64_t g_totalBytesTx = 0;

void TxTrace (Ptr<const Packet> packet)
{
  Ptr<Packet> copy = packet->Copy();
  WifiMacHeader hdr;
  if (copy->PeekHeader (hdr))
    {
      if (hdr.IsData () && hdr.GetAddr1 () == Mac48Address ("ff:ff:ff:ff:ff:ff"))
        {
          g_totalBytesTx += packet->GetSize ();
        }
    }
}

// Custom application definition
class CustomUdpBroadcastClient : public Application
{
public:
  CustomUdpBroadcastClient();
  virtual ~CustomUdpBroadcastClient();
  static TypeId GetTypeId(void);
  void SetRemote(Ipv4Address ip, uint16_t port);
  void SetData(std::string data);

private:
  virtual void StartApplication(void);
  virtual void StopApplication(void);
  void ScheduleTransmit(Time dt);
  void Send(void);

  Ptr<Socket> m_socket;
  Ipv4Address m_peerAddress;
  uint16_t m_peerPort;
  EventId m_sendEvent;
  std::string m_data;
  uint32_t m_packetSize;
  Time m_interval;
  uint32_t m_maxPackets;
  uint32_t m_packetsSent;
};

CustomUdpBroadcastClient::CustomUdpBroadcastClient()
{
  m_socket = 0;
  m_packetsSent = 0;
}

CustomUdpBroadcastClient::~CustomUdpBroadcastClient()
{
  m_socket = 0;
}

TypeId CustomUdpBroadcastClient::GetTypeId(void)
{
  static TypeId tid = TypeId("CustomUdpBroadcastClient")
    .SetParent<Application>()
    .AddConstructor<CustomUdpBroadcastClient>()
    .AddAttribute("RemoteAddress", "Destination IP address",
                  Ipv4AddressValue(),
                  MakeIpv4AddressAccessor(&CustomUdpBroadcastClient::m_peerAddress),
                  MakeIpv4AddressChecker())
    .AddAttribute("RemotePort", "Destination port",
                  UintegerValue(5000),  // Updated to 5000
                  MakeUintegerAccessor(&CustomUdpBroadcastClient::m_peerPort),
                  MakeUintegerChecker<uint16_t>())
    .AddAttribute("Interval", "Time between packets",
                  TimeValue(Seconds(0.1)),
                  MakeTimeAccessor(&CustomUdpBroadcastClient::m_interval),
                  MakeTimeChecker())
    .AddAttribute("MaxPackets", "Number of packets to send",
                  UintegerValue(100),
                  MakeUintegerAccessor(&CustomUdpBroadcastClient::m_maxPackets),
                  MakeUintegerChecker<uint32_t>())
    .AddAttribute("Data", "String data to send",
                  StringValue(""),
                  MakeStringAccessor(&CustomUdpBroadcastClient::m_data),
                  MakeStringChecker());
  return tid;
}

void CustomUdpBroadcastClient::SetRemote(Ipv4Address ip, uint16_t port)
{
  m_peerAddress = ip;
  m_peerPort = port;
}

void CustomUdpBroadcastClient::SetData(std::string data)
{
  m_data = data;
  m_packetSize = data.length();
}

void CustomUdpBroadcastClient::StartApplication(void)
{
  if (!m_socket)
  {
    TypeId tid = TypeId::LookupByName("ns3::UdpSocketFactory");
    m_socket = Socket::CreateSocket(GetNode(), tid);
    m_socket->SetAllowBroadcast(true);
    m_socket->Bind();
    m_socket->Connect(InetSocketAddress(m_peerAddress, m_peerPort));
  }
  m_packetsSent = 0;
  ScheduleTransmit(Seconds(0.));
}

void CustomUdpBroadcastClient::StopApplication()
{
  if (m_socket)
  {
    m_socket->Close();
  }
  Simulator::Cancel(m_sendEvent);
}

void CustomUdpBroadcastClient::ScheduleTransmit(Time dt)
{
  m_sendEvent = Simulator::Schedule(dt, &CustomUdpBroadcastClient::Send, this);
}

void CustomUdpBroadcastClient::Send(void)
{
  Ptr<Packet> packet = Create<Packet>((uint8_t*)m_data.c_str(), m_data.length());
  m_socket->Send(packet);
  m_packetsSent++;
  if (m_packetsSent < m_maxPackets)
  {
    ScheduleTransmit(m_interval);
  }
}

int main (int argc, char *argv[])
{
  uint32_t numStations = 10;
  double simulationTime = 10.0;
  uint16_t port = 5000;  // Updated to 5000
  double txStartTime = 2.0;

  CommandLine cmd;
  cmd.AddValue ("numStations", "Number of station nodes", numStations);
  cmd.Parse (argc, argv);

  NodeContainer staNodes;
  staNodes.Create (numStations);
  NodeContainer apNode;
  apNode.Create (1);

  WifiHelper wifi;
  wifi.SetStandard (WIFI_STANDARD_80211g);

  YansWifiChannelHelper channel = YansWifiChannelHelper::Default ();
  YansWifiPhyHelper phy;
  phy.SetChannel (channel.Create ());

  WifiMacHelper mac;
  Ssid ssid = Ssid ("ns-3-broadcast");

  mac.SetType ("ns3::StaWifiMac", "Ssid", SsidValue (ssid), "ActiveProbing", BooleanValue (false));
  NetDeviceContainer staDevices = wifi.Install (phy, mac, staNodes);

  mac.SetType ("ns3::ApWifiMac", "Ssid", SsidValue (ssid));
  NetDeviceContainer apDevice = wifi.Install (phy, mac, apNode);

  Ptr<WifiNetDevice> apWifiDevice = apDevice.Get (0)->GetObject<WifiNetDevice> ();
  apWifiDevice->GetPhy ()->TraceConnectWithoutContext ("PhyTxEnd", MakeCallback (&TxTrace));

  MobilityHelper mobility;
  mobility.SetPositionAllocator ("ns3::GridPositionAllocator", "MinX", DoubleValue (0.0), "MinY", DoubleValue (0.0), "DeltaX", DoubleValue (10.0), "DeltaY", DoubleValue (10.0), "GridWidth", UintegerValue (5));
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (staNodes);
  mobility.Install (apNode);

  InternetStackHelper stack;
  stack.Install (staNodes);
  stack.Install (apNode);

  Ipv4AddressHelper address;
  address.SetBase ("10.1.4.0", "255.255.255.0");
  NetDeviceContainer allDevices;
  allDevices.Add (staDevices);
  allDevices.Add (apDevice);
  Ipv4InterfaceContainer interfaces = address.Assign (allDevices);

  // Print IP addresses to verify network configuration
  for (uint32_t i = 0; i < allDevices.GetN(); ++i) {
      Ptr<Ipv4> ipv4 = allDevices.Get(i)->GetNode()->GetObject<Ipv4>();
      Ipv4InterfaceAddress iaddr = ipv4->GetAddress(1, 0);
      std::cout << "Node " << i << " IP: " << iaddr.GetLocal() << std::endl;
  }

  UdpServerHelper udpServer (port);
  ApplicationContainer serverApps;
  for (uint32_t i = 0; i < staNodes.GetN (); ++i)
    {
      serverApps.Add (udpServer.Install (staNodes.Get (i)));
    }
  serverApps.Start (Seconds (1.0));
  serverApps.Stop (Seconds (simulationTime + 1));

  // Replace UdpClientHelper with CustomUdpBroadcastClient
  Ptr<CustomUdpBroadcastClient> app = CreateObject<CustomUdpBroadcastClient>();
  app->SetRemote(Ipv4Address("255.255.255.255"), port);
  app->SetData("Hello, this is a broadcast message!");
  app->SetAttribute("Interval", TimeValue(Seconds(0.1)));
  app->SetAttribute("MaxPackets", UintegerValue(100));
  app->SetStartTime(Seconds(txStartTime));
  app->SetStopTime(Seconds(simulationTime));
  apNode.Get(0)->AddApplication(app);

  phy.EnablePcap ("wifi-broadcast", allDevices);

  Simulator::Stop (Seconds (simulationTime + 1));
  Simulator::Run ();
  Simulator::Destroy ();

  double txDuration = simulationTime - txStartTime;
  double avgThroughput = (g_totalBytesTx * 8.0) / (txDuration * 1e6);

  std::cout << "Total transmitted UDP broadcast bytes from AP: " << g_totalBytesTx << std::endl;
  std::cout << "Average UDP broadcast throughput of the AP: " << avgThroughput << " Mbps" << std::endl;

  return 0;
}
