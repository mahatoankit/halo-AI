from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.dashboard.models import (
    SubscriptionPlan,
    FarmerSubscription,
    FarmerFieldProfile,
    SoilHealthReport,
)
from apps.users.models import FarmerProfile
from apps.crops.models import CropPredictionRequest
from apps.sensors.models import IoTSensorSet
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Create sample data for the farmer dashboard MVP"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Creating sample data for farmer dashboard...")
        )

        # Create subscription plans
        self.create_subscription_plans()

        # Create sample farmer subscriptions and profiles
        self.create_farmer_data()

        # Create sample soil health reports
        self.create_soil_reports()

        # Create sample crop predictions
        self.create_sample_predictions()

        self.stdout.write(self.style.SUCCESS("Sample data created successfully!"))

    def create_subscription_plans(self):
        """Create subscription plans for farmers"""
        plans = [
            {
                "name": "basic",
                "display_name": "Basic Plan",
                "description": "Essential crop recommendations for small farmers",
                "price": Decimal("500.00"),
                "monthly_predictions": 10,
                "expert_consultation": False,
                "sensor_data_access": False,
                "soil_health_reports": False,
            },
            {
                "name": "premium",
                "display_name": "Premium Plan",
                "description": "Advanced features with expert consultation",
                "price": Decimal("1200.00"),
                "monthly_predictions": 25,
                "expert_consultation": True,
                "sensor_data_access": True,
                "soil_health_reports": True,
            },
            {
                "name": "gold",
                "display_name": "Gold Plan",
                "description": "Complete agricultural support with priority assistance",
                "price": Decimal("2500.00"),
                "monthly_predictions": 50,
                "expert_consultation": True,
                "sensor_data_access": True,
                "soil_health_reports": True,
            },
        ]

        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data["name"], defaults=plan_data
            )
            if created:
                self.stdout.write(f"Created subscription plan: {plan.display_name}")

    def create_farmer_data(self):
        """Create sample farmer subscriptions and field profiles"""
        try:
            # Get community admin
            community_admin = User.objects.filter(role="community_admin").first()
            if not community_admin:
                self.stdout.write(
                    self.style.WARNING("No community admin found. Creating one...")
                )
                community_admin = User.objects.create_user(
                    username="admin_bhairahawa",
                    email="admin@bhairahawa.com",
                    first_name="Bhairahawa",
                    last_name="Admin",
                    role="community_admin",
                    assigned_region="Bhairahawa-Butwal",
                )

            # Get farmers
            farmers = User.objects.filter(role="farmer")[:3]

            if not farmers.exists():
                # Create sample farmers
                farmer_data = [
                    {
                        "username": "farmer_krishna",
                        "email": "krishna@farmer.com",
                        "first_name": "Krishna",
                        "last_name": "Thapa",
                    },
                    {
                        "username": "farmer_sita",
                        "email": "sita@farmer.com",
                        "first_name": "Sita",
                        "last_name": "Sharma",
                    },
                    {
                        "username": "farmer_ram",
                        "email": "ram@farmer.com",
                        "first_name": "Ram",
                        "last_name": "Poudel",
                    },
                ]

                farmers = []
                for data in farmer_data:
                    farmer = User.objects.create_user(
                        password="demo123", role="farmer", **data
                    )
                    farmers.append(farmer)
                    self.stdout.write(f"Created farmer: {farmer.get_full_name()}")

            # Get subscription plans
            basic_plan = SubscriptionPlan.objects.get(name="basic")
            premium_plan = SubscriptionPlan.objects.get(name="premium")
            gold_plan = SubscriptionPlan.objects.get(name="gold")

            plans = [basic_plan, premium_plan, gold_plan]

            for i, farmer in enumerate(farmers[:3]):
                # Create subscription
                subscription, created = FarmerSubscription.objects.get_or_create(
                    farmer=farmer,
                    defaults={
                        "plan": plans[i % 3],
                        "community_admin": community_admin,
                        "start_date": timezone.now() - timedelta(days=15),
                        "end_date": timezone.now() + timedelta(days=15),
                        "status": "active",
                        "predictions_used": i * 3 + 2,  # Some usage
                    },
                )
                if created:
                    self.stdout.write(
                        f"Created subscription for {farmer.get_full_name()}"
                    )

                # Create field profile
                profile, created = FarmerFieldProfile.objects.get_or_create(
                    farmer=farmer,
                    defaults={
                        "region": "Bhairahawa",
                        "district": "Rupandehi",
                        "local_unit": f"Municipality-{i+1}",
                        "total_area": Decimal(
                            str(2.5 + i * 1.5)
                        ),  # Different farm sizes
                        "soil_type": ["Clay Loam", "Sandy Loam", "Loam"][i],
                        "irrigation_type": ["canal", "tubewell", "rain_fed"][i],
                        "primary_crops": [
                            "Rice, Wheat",
                            "Maize, Potato",
                            "Rice, Mustard",
                        ][i],
                        "secondary_crops": ["Lentils", "Vegetables", "Sugarcane"][i],
                        "organic_farming": i == 1,  # One farmer uses organic methods
                        "experience_years": 10 + i * 5,
                    },
                )
                if created:
                    self.stdout.write(
                        f"Created field profile for {farmer.get_full_name()}"
                    )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating farmer data: {str(e)}"))

    def create_soil_reports(self):
        """Create sample soil health reports using MVP parameters"""
        farmers = User.objects.filter(role="farmer")[:3]

        # MVP soil parameters based on Bhairahawa region
        # N, P, K averages: 30, 22.5, 60
        # pH: 6.0 (from regional data)
        soil_data = [
            {
                "nitrogen": 32.5,
                "phosphorus": 24.0,
                "potassium": 58.0,
                "ph": 6.2,
                "organic_matter": 2.8,
                "health_score": 85.0,
            },
            {
                "nitrogen": 28.0,
                "phosphorus": 21.0,
                "potassium": 62.5,
                "ph": 5.8,
                "organic_matter": 3.2,
                "health_score": 78.0,
            },
            {
                "nitrogen": 35.0,
                "phosphorus": 23.5,
                "potassium": 65.0,
                "ph": 6.5,
                "organic_matter": 3.8,
                "health_score": 92.0,
            },
        ]

        for i, farmer in enumerate(farmers):
            if i < len(soil_data):
                report, created = SoilHealthReport.objects.get_or_create(
                    farmer=farmer,
                    test_date=timezone.now().date() - timedelta(days=30),
                    defaults={
                        "report_type": "lab_test",
                        "lab_name": "Bhairahawa Agricultural Lab",
                        **soil_data[i],
                        "recommendations": self.get_soil_recommendations(soil_data[i]),
                        "deficiencies": self.get_deficiencies(soil_data[i]),
                    },
                )
                if created:
                    self.stdout.write(
                        f"Created soil report for {farmer.get_full_name()}"
                    )

    def get_soil_recommendations(self, soil_data):
        """Generate soil recommendations based on data"""
        recommendations = []

        if soil_data["ph"] < 6.0:
            recommendations.append("Apply lime to increase soil pH")
        elif soil_data["ph"] > 7.0:
            recommendations.append("Consider adding organic matter to balance pH")

        if soil_data["nitrogen"] < 25:
            recommendations.append("Apply nitrogen-rich fertilizer or compost")
        elif soil_data["nitrogen"] > 40:
            recommendations.append(
                "Reduce nitrogen input to prevent nutrient imbalance"
            )

        if soil_data["organic_matter"] < 3.0:
            recommendations.append(
                "Increase organic matter through compost and crop residues"
            )

        if not recommendations:
            recommendations.append("Soil health is good. Maintain current practices.")

        return ". ".join(recommendations)

    def get_deficiencies(self, soil_data):
        """Identify nutrient deficiencies"""
        deficiencies = []

        # Based on ideal ranges for the region
        if soil_data["nitrogen"] < 30:
            deficiencies.append("nitrogen")
        if soil_data["phosphorus"] < 20:
            deficiencies.append("phosphorus")
        if soil_data["potassium"] < 50:
            deficiencies.append("potassium")
        if soil_data["organic_matter"] < 3.0:
            deficiencies.append("organic_matter")

        return deficiencies

    def create_sample_predictions(self):
        """Create sample crop prediction data"""
        self.stdout.write("Creating sample crop predictions...")

        # Get community admin user
        try:
            community_admin = User.objects.get(username="community_admin_bhairahawa")
        except User.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("Community admin not found, skipping predictions")
            )
            return

        # Get or create sample sensor set
        sensor_set, created = IoTSensorSet.objects.get_or_create(
            name="Bhairahawa-Field-01",
            defaults={
                "community_admin": community_admin,
                "location": "Bhairahawa, Rupandehi",
                "device_type": "multi_sensor",
                "installation_date": timezone.now().date() - timedelta(days=30),
                "status": "active",
            },
        )

        # Sample crop prediction data
        sample_predictions = [
            {
                "predicted_crops": [
                    {
                        "crop": "rice",
                        "confidence": 0.87,
                        "supporting_models": ["xgboost", "random_forest"],
                    },
                    {"crop": "wheat", "confidence": 0.65, "supporting_models": ["svm"]},
                    {
                        "crop": "maize",
                        "confidence": 0.43,
                        "supporting_models": ["random_forest"],
                    },
                ],
                "nitrogen": 85.0,
                "phosphorus": 45.0,
                "potassium": 55.0,
                "temperature": 26.5,
                "humidity": 78.0,
                "ph": 6.2,
                "rainfall": 180.0,
                "status": "completed",
                "confidence_score": 0.87,
                "days_ago": 2,
            },
            {
                "predicted_crops": [
                    {
                        "crop": "maize",
                        "confidence": 0.92,
                        "supporting_models": ["xgboost", "random_forest", "svm"],
                    },
                    {
                        "crop": "sugarcane",
                        "confidence": 0.71,
                        "supporting_models": ["xgboost", "random_forest"],
                    },
                    {"crop": "rice", "confidence": 0.58, "supporting_models": ["svm"]},
                ],
                "nitrogen": 65.0,
                "phosphorus": 35.0,
                "potassium": 40.0,
                "temperature": 28.0,
                "humidity": 65.0,
                "ph": 6.8,
                "rainfall": 120.0,
                "status": "completed",
                "confidence_score": 0.92,
                "days_ago": 5,
            },
            {
                "predicted_crops": [
                    {
                        "crop": "wheat",
                        "confidence": 0.79,
                        "supporting_models": ["random_forest", "svm"],
                    },
                    {
                        "crop": "mustard",
                        "confidence": 0.68,
                        "supporting_models": ["xgboost"],
                    },
                    {
                        "crop": "barley",
                        "confidence": 0.54,
                        "supporting_models": ["svm"],
                    },
                ],
                "nitrogen": 70.0,
                "phosphorus": 40.0,
                "potassium": 45.0,
                "temperature": 22.0,
                "humidity": 70.0,
                "ph": 7.1,
                "rainfall": 95.0,
                "status": "completed",
                "confidence_score": 0.79,
                "days_ago": 7,
            },
            {
                "predicted_crops": [],
                "nitrogen": 75.0,
                "phosphorus": 50.0,
                "potassium": 60.0,
                "temperature": 25.0,
                "humidity": 75.0,
                "ph": 6.5,
                "rainfall": 200.0,
                "status": "processing",
                "confidence_score": None,
                "days_ago": 1,
            },
        ]

        for pred_data in sample_predictions:
            # Create the prediction request
            prediction = CropPredictionRequest.objects.create(
                community_admin=community_admin,
                sensor_set=sensor_set,
                nitrogen=pred_data["nitrogen"],
                phosphorus=pred_data["phosphorus"],
                potassium=pred_data["potassium"],
                temperature=pred_data["temperature"],
                humidity=pred_data["humidity"],
                ph=pred_data["ph"],
                rainfall=pred_data["rainfall"],
                status=pred_data["status"],
                predicted_crops=pred_data["predicted_crops"],
                confidence_score=pred_data["confidence_score"],
                model_version="v1.0",
            )

            # Set the requested_at to simulate older predictions
            prediction.requested_at = timezone.now() - timedelta(
                days=pred_data["days_ago"]
            )
            if pred_data["status"] == "completed":
                prediction.processed_at = prediction.requested_at + timedelta(
                    minutes=random.randint(5, 30)
                )
            prediction.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(sample_predictions)} sample crop predictions"
            )
        )
