"""
Seed Service - Poblar datos iniciales
"""
from sqlalchemy.orm import Session
from app.database.models import CustomerDB, CountryDB, ChannelDB, MerchantDB


class SeedService:
    """Servicio para poblar datos iniciales"""
    
    @staticmethod
    def seed_countries(db: Session):
        """Poblar países"""
        countries = [
            {"code": "PE", "name": "Perú", "currency": "PEN"},
            {"code": "BR", "name": "Brasil", "currency": "BRL"},
            {"code": "CL", "name": "Chile", "currency": "CLP"},
        ]
        
        existing_count = db.query(CountryDB).count()
        if existing_count > 0:
            print(f"   ⏭️  Países ya poblados ({existing_count} registros)")
            return
        
        for country_data in countries:
            country = CountryDB(**country_data)
            db.add(country)
        
        db.commit()
        print(f"   ✅ {len(countries)} países insertados")
    
    @staticmethod
    def seed_channels(db: Session):
        """Poblar canales"""
        channels = [
            {"code": "web", "name": "Web", "description": "Banca por Internet"},
            {"code": "mobile", "name": "Mobile", "description": "App Móvil"},
            {"code": "atm", "name": "ATM", "description": "Cajero Automático"},
            {"code": "branch", "name": "Branch", "description": "Sucursal Física"},
        ]
        
        existing_count = db.query(ChannelDB).count()
        if existing_count > 0:
            print(f"   ⏭️  Canales ya poblados ({existing_count} registros)")
            return
        
        for channel_data in channels:
            channel = ChannelDB(**channel_data)
            db.add(channel)
        
        db.commit()
        print(f"   ✅ {len(channels)} canales insertados")
    
    @staticmethod
    def seed_customers(db: Session):
        """Poblar clientes"""
        customers = [
            {
                "customer_id": "CU-001",
                "nombre": "Juan Carlos",
                "apellido": "Pérez García",
                "email": "juan.perez@email.com",
                "telefono": "+51 987654321"
            },
            {
                "customer_id": "CU-002",
                "nombre": "María Elena",
                "apellido": "Rodríguez López",
                "email": "maria.rodriguez@email.com",
                "telefono": "+51 987654322"
            }
        ]
        
        existing_count = db.query(CustomerDB).count()
        if existing_count > 0:
            print(f"   ⏭️  Clientes ya poblados ({existing_count} registros)")
            return
        
        for customer_data in customers:
            customer = CustomerDB(**customer_data)
            db.add(customer)
        
        db.commit()
        print(f"   ✅ {len(customers)} clientes insertados")
    
    @staticmethod
    def seed_merchants(db: Session):
        """Poblar comercios"""
        merchants = [
            {
                "merchant_id": "M-001",
                "nombre": "Supermercados Wong",
                "categoria": "Supermercado",
                "pais": "PE"
            },
            {
                "merchant_id": "M-002",
                "nombre": "Saga Falabella",
                "categoria": "Tienda por Departamento",
                "pais": "PE"
            },
            {
                "merchant_id": "M-003",
                "nombre": "Amazon Perú",
                "categoria": "E-commerce",
                "pais": "PE"
            },
            {
                "merchant_id": "M-004",
                "nombre": "Restaurante Central",
                "categoria": "Restaurante",
                "pais": "PE"
            },
            {
                "merchant_id": "M-005",
                "nombre": "Cineplanet",
                "categoria": "Entretenimiento",
                "pais": "PE"
            },
            {
                "merchant_id": "M-999",
                "nombre": "Comercio Desconocido",
                "categoria": "Desconocido",
                "pais": "BR"
            },
        ]
        
        existing_count = db.query(MerchantDB).count()
        if existing_count > 0:
            print(f"   ⏭️  Comercios ya poblados ({existing_count} registros)")
            return
        
        for merchant_data in merchants:
            merchant = MerchantDB(**merchant_data)
            db.add(merchant)
        
        db.commit()
        print(f"   ✅ {len(merchants)} comercios insertados")
    
    @staticmethod
    def seed_all(db: Session):
        """Poblar todos los datos maestros"""
        print("\n🌱 Poblando datos maestros...")
        SeedService.seed_countries(db)
        SeedService.seed_channels(db)
        SeedService.seed_customers(db)
        SeedService.seed_merchants(db)
        print("✅ Datos maestros poblados\n")