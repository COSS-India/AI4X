# Kong API Gateway Architecture Diagram Specification

## For Eraser.io or Draw.io

### 🎯 **Diagram Components & Layout**

#### **1. Top Layer - External Users**
```
┌─────────────────────────────────────┐
│         INTERNET / USERS            │
│                                     │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ Dhruva App  │  │ External    │   │
│  │ (Frontend)  │  │ Clients     │   │
│  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────┘
```

#### **2. Load Balancer / Nginx Layer**
```
┌─────────────────────────────────────┐
│         NGINX REVERSE PROXY         │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ • SSL/TLS Termination           │ │
│  │ • Security Headers              │ │
│  │ • Rate Limiting                 │ │
│  │ • Gzip Compression              │ │
│  │ • Health Checks                 │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

#### **3. API Gateway Layer**
```
┌─────────────────────────────────────┐
│         KONG API GATEWAY            │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ • API Key Authentication        │ │
│  │ • Rate Limiting (per service)   │ │
│  │ • CORS Handling                 │ │
│  │ • Request/Response Transform    │ │
│  │ • Load Balancing                │ │
│  │ • Health Checks                 │ │
│  │ • Metrics & Logging             │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

#### **4. Service Routing Layer**
```
┌─────────────────────────────────────┐
│         SERVICE ROUTING             │
│                                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │   /asr  │ │   /tts  │ │/translation│ │
│  │100 req/m│ │ 50 req/m│ │200 req/m│ │
│  └─────────┘ └─────────┘ └─────────┘ │
│                                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │   /api  │ │  /other │ │  /admin │ │
│  │1000 req/m│ │services│ │  /health│ │
│  └─────────┘ └─────────┘ └─────────┘ │
└─────────────────────────────────────┘
```

#### **5. AI Models Layer (EC2 Instance)**
```
┌─────────────────────────────────────┐
│    AI MODELS (EC2: 172.31.31.208)   │
│                                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │ ASR     │ │ TTS     │ │Translation│ │
│  │:5000    │ │:9000    │ │:8000    │ │
│  └─────────┘ └─────────┘ └─────────┘ │
│                                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │Backend  │ │ Other   │ │Monitoring│ │
│  │:8000    │ │Services │ │Services │ │
│  └─────────┘ └─────────┘ └─────────┘ │
└─────────────────────────────────────┘
```

#### **6. Database Layer**
```
┌─────────────────────────────────────┐
│         DATABASE LAYER              │
│                                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │MongoDB  │ │PostgreSQL│ │Timescale│ │
│  │API Keys │ │Kong DB  │ │Metrics  │ │
│  └─────────┘ └─────────┘ └─────────┘ │
│                                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │ Redis   │ │RabbitMQ │ │ Logs    │ │
│  │Cache    │ │Queue    │ │Storage  │ │
│  └─────────┘ └─────────┘ └─────────┘ │
└─────────────────────────────────────┘
```

#### **7. Management & Monitoring Layer**
```
┌─────────────────────────────────────┐
│    MANAGEMENT & MONITORING          │
│                                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │Kong Admin│ │Kong Mgr │ │API Mgr  │ │
│  │:8001    │ │:8002    │ │:8080    │ │
│  └─────────┘ └─────────┘ └─────────┘ │
│                                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │Prometheus│ │ Grafana │ │Alerts   │ │
│  │:9090    │ │:3000    │ │Manager  │ │
│  └─────────┘ └─────────┘ └─────────┘ │
└─────────────────────────────────────┘
```

### 🔄 **Connection Flow**

#### **Request Flow (Blue Arrows)**
```
Users → Nginx → Kong → Services → AI Models
```

#### **Response Flow (Green Arrows)**
```
AI Models → Services → Kong → Nginx → Users
```

#### **Management Flow (Orange Arrows)**
```
Management → Kong Admin → Kong Gateway
Management → API Manager → MongoDB
Monitoring → Prometheus → All Services
```

### 🎨 **Color Scheme**

- **Blue**: External/Internet components
- **Green**: API Gateway and routing
- **Orange**: AI Models and services
- **Purple**: Database layer
- **Red**: Management and monitoring
- **Gray**: Security and infrastructure

### 📐 **Layout Instructions**

1. **Vertical Stack**: Arrange components from top to bottom
2. **Horizontal Alignment**: Center-align all components
3. **Spacing**: Equal spacing between layers (50px)
4. **Connections**: Use arrows to show data flow
5. **Labels**: Add port numbers and descriptions

### 🔧 **For Draw.io Specific Instructions**

1. **Create New Diagram**: Choose "Blank Diagram"
2. **Add Shapes**: Use rectangles for components
3. **Add Text**: Include service names and ports
4. **Add Arrows**: Use connection arrows between components
5. **Group Components**: Group related services together
6. **Add Colors**: Apply color scheme as specified

### 🎯 **For Eraser.io Specific Instructions**

1. **Create New Project**: Start with blank canvas
2. **Add Components**: Use rectangle shapes
3. **Layer Organization**: Use layers for different components
4. **Connections**: Draw arrows between components
5. **Styling**: Apply consistent colors and fonts
6. **Export**: Save as PNG/SVG for documentation

### 📋 **Key Information to Include**

#### **Port Mappings**
- Nginx: 80 (HTTP), 443 (HTTPS)
- Kong Proxy: 8000
- Kong Admin: 8001
- Kong Manager: 8002
- API Manager: 8080
- Prometheus: 9090
- Grafana: 3000

#### **Service Endpoints**
- ASR: https://your-ip/asr
- TTS: https://your-ip/tts
- Translation: https://your-ip/translation
- Backend API: https://your-ip/api

#### **Rate Limits**
- ASR: 100 requests/minute
- TTS: 50 requests/minute
- Translation: 200 requests/minute
- Backend: 1000 requests/minute

### 🚀 **Quick Start for Draw.io**

1. Go to [app.diagrams.net](https://app.diagrams.net)
2. Create new diagram
3. Add these shapes in order:
   - Rectangle: "Internet/Users"
   - Rectangle: "Nginx Reverse Proxy"
   - Rectangle: "Kong API Gateway"
   - Rectangle: "Service Routing"
   - Rectangle: "AI Models (EC2)"
   - Rectangle: "Database Layer"
   - Rectangle: "Management & Monitoring"
4. Connect with arrows
5. Add labels and port numbers
6. Apply colors
7. Save and export

### 🎨 **Quick Start for Eraser.io**

1. Go to [app.eraser.io](https://app.eraser.io)
2. Create new project
3. Use the component specifications above
4. Draw rectangles for each layer
5. Add connection arrows
6. Include port numbers and descriptions
7. Apply the color scheme
8. Export as needed

This specification provides everything you need to create a professional architecture diagram in either tool!
